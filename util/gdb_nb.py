import json
import re
import numpy as np
from IPython.display import display, HTML
from pathlib import Path

def _msg_html(command: str, results: list):
    # Define colors based on response type
    colors = {
        "result": "#388E3C",  # Green
        "notify": "#1976D2",  # Blue
        "console": "#000000",  # Black
        "log": "#757575",  # Gray
        "output": "#D32F2F",  # Red
        "target": "#7B1FA2",  # Purple
        "done": "#388E3C",  # Green
    }

    # Build the command header with a monospace gray background
    command_html = f"""
        <div style="
            font-family: monospace;
            font-size: 12px;
            background: #f5f5f5;
            padding: 0.5em;
            border-radius: 4px;
            margin-bottom: 0.75em;
        ">
            {command}
        </div>
    """

    # Build the list of responses
    responses_html = ""
    for result in results:
        response_type = result.get("type", "console")
        color = colors.get(response_type, "#000000")  # Default to black if type is unknown

        # If is a console response, just use the payload as message
        if result.get("type") == "console":
            result["message"] = result["payload"]
            result["payload"] = None

        # Build the message HTML
        msg_html = ""
        msg = result.get("message", None)
        if msg is not None:
            msg_html = f"""
                <div style="
                    font-size: 12px;
                    margin-bottom: 0.25em;
                    color: rgba(0, 0, 0, 0.87);
                    ">
                    {msg}
                </div>
            """

        # Build the payload HTML
        payload_html = ""
        payload = result.get("payload", None)
        if payload is not None:
            payload_html = f"""
                <pre style="
                    background: #f5f5f5;
                    padding: 0.5em;
                    border-radius: 4px;
                    margin: 0 0 0.5em 0;
                    font-size: 11px;
                    color: #333;
                    line-height: 1.3;
                ">{json.dumps(payload, indent=2).strip()}
                </pre>
            """

        # Combine message and payload for this response
        responses_html += f"""
            <div style="
                margin-bottom: 0.5em;
                border-left: 4px solid {color};
                padding-left: 0.5em;
            ">
                <span style="
                    font-size: 11px;
                    font-weight: bold;
                    color: {color};
                    text-transform: uppercase;
                ">
                    {response_type}
                </span>
                {msg_html}
                {payload_html}
            </div>
        """

    # Combine everything into a condensed view
    return f"""
        <div style="
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 0.75em;
            margin: 0.5em 0;
            background: #ffffff;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            font-family: Arial, sans-serif;
            color: rgba(0, 0, 0, 0.87);
        ">
            {command_html}
            <div style="margin-left: 0.5em;">
                {responses_html}
            </div>
        </div>
    """

def cmd(gdb, body):
    responses = gdb.write(body)
    display(HTML(_msg_html(body, responses)))

def _source_code(source_content: str, target_line: int, pad: int = 5):
    # Split the source content into lines
    lines = source_content.splitlines()

    # Calculate the range of lines to display
    start_line = max(1, target_line - pad)
    end_line = min(len(lines), target_line + pad)

    # Crop the lines to the specified range
    cropped_lines = lines[start_line - 1 : end_line]

    # Generate HTML for the cropped source content
    source_html = ""
    for i, line in enumerate(cropped_lines, start=start_line):
        # Highlight the target line
        background_style = ""
        if i == target_line:
            background_style="background: #fff3e0;"
        source_html += f"""
            <span style="padding: 0.25em 0; display: block;{background_style}">
                <span style="display: inline-block; width: 4em; text-align: right; color: #757575; margin-right: 1em;">{i}</span>
                <span style="font-family: monospace;">{line}</span>
            </span>
        """

    # Wrap the source content in a CSS grid container
    return source_html

def _source_html(source_content: str, file_path: str, function_name: str, line_number: int):

    # Generate HTML for the source file content
    source_html = _source_code(source_content, line_number)

    # Generate HTML for the paused state information
    info_html = f"""
        <div style="
            display: flex;
            border-bottom: 1px solid #e0e0e0;
            padding: 0.25em;
            color: rgba(0, 0, 0, 0.87);
            font-family: monospace;">
            <span style="flex: 1;">{file_path}</span>
            <span>fn: {function_name} @ line: {line_number}</span>
        </div>
    """

    # Combine everything into a final HTML output
    html_output = f"""
            <div style="
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 0.5em;
                background: #fafafa;
                font-family: Arial, sans-serif;
                font-size: 0.8em;
                color: rgba(0, 0, 0, 0.87);
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
            ">
                {info_html}
                {source_html}
            </div>
        </div>
    """

    return html_output

def get_result(gdb, cmd):
    for resp in gdb.write(cmd):
        if resp["type"] == "result":
            return resp

def show_current_location(gdb, use_source=None):
    resp = get_result(gdb, "-stack-info-frame")
    if resp is None:
        raise Exception("Missing result response")
    frame = resp["payload"]["frame"]

    source = use_source
    path = frame["file"]
    fullpath = frame["fullname"]
    fn = frame["func"]
    line = int(frame["line"])
    if use_source is None:
        source = Path(fullpath).read_text()

    display(HTML(_source_html(source, path, fn, line)))

def run_or_raise(gdb, cmd):
    res = get_result(gdb, cmd)
    if res is not None and res.get("message") == "error":
        raise Exception(res.get("payload", {}).get("msg"))
    return res

type_re = re.compile(r"(\w+)(\((\w+=[\d*]+,?)*\))?\s*(\((\d+,?)*\))?")
def get_variable_type(gdb, name, temp_name = "temp__"):
    run_or_raise(gdb, f"-var-create {temp_name} * {name}")
    typ = None
    try:
        res = get_result(gdb, f"-var-info-type {temp_name}")
        if res is None:
            return
        typ = res.get("payload", {}).get("type", None)
    finally:
        gdb.write(f"-var-delete {temp_name}")

    # parse type
    if typ is None:
        return 

    if (match := type_re.match(typ)) is not None:
        info = {
            "type": match.group(1).lower(),
        }

        if (parms := match.group(2)) is not None:
            for parm in parms.strip("()").split(","):
                name, value = parm.split("=")
                try:
                    value = int(value)
                except:
                    pass 
                info[name] = value 

        if (shape := match.group(4)) is not None:
            parsed_shape = []
            for component in shape.strip("()").split(","):
                parsed_shape += [int(component)]
            info["shape"] = parsed_shape
            
        return info

def load_array(gdb, name):
    info = get_variable_type(gdb, name)
    if info is None:
        raise Exception(f"Could not probe variable '{name}' info")

    dtype = np.float32 
    if info.get("type") == "real":
        kind = int(info.get("kind", 4))
        if kind == 4:
            dtype = np.float32
        elif kind == 8:
            dtype = np.float64 
    elif info.get("type") == "integer":
        dtype = np.int8
    else:
        raise Exception(f"Unhandled type '{info.get('type')}' for variable '{name}'")

    size = 1 
    shape = info.get("shape", [])
    for comp in shape:
        size *= comp

    # create array
    arr = np.zeros((size), dtype=dtype)
    
    # fetch and parse
    resp = run_or_raise(gdb, f"-data-evaluate-expression {name}")
    k = 0
    value = resp.get("payload").get("value").strip("()").replace(") (", ", ")
    for value in value.split(","):
        try:
            arr[k] = dtype(value)
        except:
            arr[k] = np.nan
        k += 1

    arr = arr.reshape(shape, order='F')
    return arr



