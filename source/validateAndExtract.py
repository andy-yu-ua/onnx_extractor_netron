from flask import Flask
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

import sys, os
# Remove the directory containing this script from sys.path if it causes a conflict.
this_dir = os.path.dirname(os.path.abspath(__file__))
if this_dir in sys.path:
    sys.path.remove(this_dir)

from flask import request, jsonify, send_file
import onnx
import onnx.helper
import os
import tempfile
import argparse

# Path to your original ONNX model file
MODEL_FILE = None

def parse_args():
    parser = argparse.ArgumentParser(description='Flask server for ONNX extraction.')
    parser.add_argument('--model', metavar='MODEL_FILE', help='Model file to serve', required=True)
    return parser.parse_args()

def validate_and_extract_subgraph(selected_node_ids):
    # Remove the prefix "node-name-" if present
    cleaned_ids = [node_id.replace("node-name-", "") for node_id in selected_node_ids]
    
    # Load the original ONNX model
    model = onnx.load(MODEL_FILE)
    
    # Filter nodes based on cleaned node names
    selected_nodes = [node for node in model.graph.node if node.name in cleaned_ids]
    if not selected_nodes:
        raise ValueError("No nodes selected or selected nodes not found in the model.")
    
    # Build mapping: tensor -> producing node (for selected nodes)
    tensor_producers = {}
    for node in selected_nodes:
        for out in node.output:
            tensor_producers[out] = node.name
    
    # Build a mapping for all initializers in the original model
    model_initializers = {init.name: init for init in model.graph.initializer}
    
    # For each selected node, if an input is not produced by a selected node,
    # add it as an external input.
    subgraph_inputs_names = set()
    for node in selected_nodes:
        for inp in node.input:
            if inp not in tensor_producers:
                subgraph_inputs_names.add(inp)
    
    # Separate constant initializers from external inputs.
    subgraph_initializers = []
    constant_input_names = set()
    for inp in list(subgraph_inputs_names):
        if inp in model_initializers:
            subgraph_initializers.append(model_initializers[inp])
            constant_input_names.add(inp)
    subgraph_inputs_names = subgraph_inputs_names - constant_input_names
    
    # Build the subgraph's input value info.
    subgraph_inputs = []
    def get_value_info(tensor_name):
        for inp in model.graph.input:
            if inp.name == tensor_name:
                return inp
        for vi in model.graph.value_info:
            if vi.name == tensor_name:
                return vi
        return onnx.helper.make_tensor_value_info(tensor_name, onnx.TensorProto.FLOAT, None)
    for inp in subgraph_inputs_names:
        subgraph_inputs.append(get_value_info(inp))
    
    # Determine subgraph outputs: outputs from selected nodes that are not used as inputs internally.
    selected_node_outputs = set()
    for node in selected_nodes:
        selected_node_outputs.update(node.output)
    
    internal_consumed = set()
    for node in selected_nodes:
        for inp in node.input:
            if inp in tensor_producers:
                internal_consumed.add(inp)
    
    subgraph_outputs_names = list(selected_node_outputs - internal_consumed)
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
    
    # Optionally, print debug info:
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