import subprocess
import sys
import signal

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_subnetron.py <model_path>")
        sys.exit(1)

    model_path = sys.argv[1]

    processes = []

    try:
        # Start Netron
        netron_cmd = ['python', 'package.py', 'build', 'start', '--browse', model_path]
        netron_proc = subprocess.Popen(netron_cmd)
        processes.append(netron_proc)

        # Start validateAndExtract
        extract_cmd = ['python', 'source/validateAndExtract.py', '--model', model_path]
        extract_proc = subprocess.Popen(extract_cmd)
        processes.append(extract_proc)

        # Wait for both to complete (or get interrupted)
        for proc in processes:
            proc.wait()

    except KeyboardInterrupt:
        print("\nCaught Ctrl+C. Terminating subprocesses...")
        for proc in processes:
            proc.terminate()
        for proc in processes:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()

    print("All processes exited.")

if __name__ == "__main__":
    main()
