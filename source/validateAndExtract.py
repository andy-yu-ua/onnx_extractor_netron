import sys
import argparse
import tempfile
import os
import onnx.helper
import onnx
from flask import request, jsonify, send_file
from flask import Flask
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

# Remove the directory containing this script from sys.path
# to avoid importing onnx from wrong place (from the source directory)
this_dir = os.path.dirname(os.path.abspath(__file__))
if this_dir in sys.path:
    sys.path.remove(this_dir)


MODEL_FILE = None


def parse_args():
    parser = argparse.ArgumentParser(
        description='Flask server for ONNX extraction.')
    parser.add_argument('--model', metavar='MODEL_FILE',
                        help='Model file to serve', required=True)
    return parser.parse_args()


def validate_and_extract_subgraph(selected_node_ids):
    # Remove the prefix "node-name-" if present
    cleaned_ids = [node_id.replace("node-name-", "") for node_id in selected_node_ids if node_id is not None]

    model = onnx.load(MODEL_FILE)

    # Filter nodes that are selected.
    selected_nodes = [node for node in model.graph.node if node.name in cleaned_ids]
    if not selected_nodes:
        raise ValueError("No nodes selected or selected nodes not found in the model.")

    # Create a mapping: tensor name -> producing node name (for selected nodes).
    tensor_producers = {}
    for node in selected_nodes:
        for out in node.output:
            tensor_producers[out] = node.name

    # Map all initializers in the original model.
    model_initializers = {init.name: init for init in model.graph.initializer}

    # Identify external inputs from selected nodes (inputs that aren't produced by a selected node).
    subgraph_inputs_names = set()
    for node in selected_nodes:
        for inp in node.input:
            if inp not in tensor_producers:
                subgraph_inputs_names.add(inp)

    # Separate and preserve constant initializers (present in the model's initializers).
    subgraph_initializers = []
    constant_input_names = set()

    for inp in list(subgraph_inputs_names):
        if inp in model_initializers:
            subgraph_initializers.append(model_initializers[inp])
            constant_input_names.add(inp)
    # Remove these constant inputs from the external inputs list.
    subgraph_inputs_names = subgraph_inputs_names - constant_input_names

    # For constant nodes (op_type 'Constant'), we want to include their output tensor (from the "value" attribute)
    # if that output is used by a selected node, even if it's not captured above.
    for node in model.graph.node:
        if node.op_type == 'Constant':
            for out in node.output:
                if (node.name in cleaned_ids or out in subgraph_inputs_names or out in tensor_producers) and out not in constant_input_names:
                    for attr in node.attribute:
                        if attr.name == "value":
                            tensor = attr.t
                            # If the tensor doesn't have a name, set it to the output name
                            if not tensor.name:
                                tensor.name = out
                            subgraph_initializers.append(tensor)
                            constant_input_names.add(out)
                            print(f"Added constant from Constant node '{node.name}' with output '{out}' as initializer.")
                            break

    # Build the subgraph's input value info.
    subgraph_inputs = []
    def get_value_info(tensor_name):
        for inp in model.graph.input:
            if inp.name == tensor_name:
                return inp
        for vi in model.graph.value_info:
            if vi.name == tensor_name:
                return vi
        # Fall back to making a new value info with float type.
        return onnx.helper.make_tensor_value_info(tensor_name, onnx.TensorProto.FLOAT, None)
    for inp in subgraph_inputs_names:
        subgraph_inputs.append(get_value_info(inp))

    # Determine subgraph outputs: collect outputs from selected nodes.
    selected_node_outputs = set()
    for node in selected_nodes:
        selected_node_outputs.update(node.output)

    # Determine which outputs are "internally consumed" (used as input by another selected node)
    internal_consumed = set()
    for node in selected_nodes:
        for inp in node.input:
            if inp in tensor_producers:
                internal_consumed.add(inp)

    # Get the names of the original model's outputs.
    original_outputs = set(out.name for out in model.graph.output)

    # Final subgraph outputs: include outputs that
    # - are not internally consumed OR
    # - are part of the original model's outputs.
    subgraph_outputs_names = list((selected_node_outputs - internal_consumed) | (selected_node_outputs & original_outputs))
    subgraph_outputs = []
    def get_output_value_info(tensor_name):
        for out in model.graph.output:
            if out.name == tensor_name:
                return out
        for vi in model.graph.value_info:
            if vi.name == tensor_name:
                return vi
        return onnx.helper.make_tensor_value_info(tensor_name, onnx.TensorProto.FLOAT, None)
    for out in subgraph_outputs_names:
        subgraph_outputs.append(get_output_value_info(out))

    # Optional debugging output
    print("Subgraph Inputs:", [inp.name for inp in subgraph_inputs])
    print("Subgraph Outputs:", [out.name for out in subgraph_outputs])
    print("Subgraph Constant Initializers:", [init.name for init in subgraph_initializers])

    # Build the new graph.
    new_graph = onnx.helper.make_graph(
        nodes=selected_nodes,
        name="extracted_subgraph",
        inputs=subgraph_inputs,
        outputs=subgraph_outputs,
        initializer=subgraph_initializers
    )
    new_model = onnx.helper.make_model(new_graph)
    return new_model

@app.route('/validate_extract', methods=['POST'])
def validate_extract():
    data = request.get_json()
    print("Received data:", data)  # Debug: log the incoming JSON payload
    selected_nodes = data.get('selectedNodes', [])
    try:
        new_model = validate_and_extract_subgraph(selected_nodes)
    except Exception as e:
        print("Error during validation/extraction:", e)
        return jsonify({'success': False, 'error': str(e)}), 400
    temp_file = os.path.join(tempfile.gettempdir(), "extracted_subgraph.onnx")
    onnx.save(new_model, temp_file)
    return send_file(temp_file, as_attachment=True)


if __name__ == '__main__':
    args = parse_args()
    MODEL_FILE = args.model
    app.run(port=5000)
