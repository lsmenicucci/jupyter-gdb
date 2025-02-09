from pygdbmi.gdbcontroller import GdbController 
import numpy as np
from rich import print, inspect

gdbmi = GdbController()
gdbmi.write("-gdb-set max-value-size unlimited")
gdbmi.write("-gdb-set max-composite-size unlimited")
gdbmi.write("-gdb-set print repeats 0")
gdbmi.write("-gdb-set print elements 0")

# start inferior
print(gdbmi.write("-file-exec-and-symbols ./test/simple"))

print(gdbmi.write(f"-break-insert simple.f90:8"))
print(gdbmi.write("-exec-run"))

def get_variable(name) -> str:
    msgs = gdbmi.write(f"-data-evaluate-expression {name}")
    for msg in msgs:
        if msg["type"] == "result":
            if "value" in msg["payload"]:
                return msg["payload"]["value"]
            else:
                return msg

def read_array_variable(name, dtype=np.float64):
    output = get_variable(name)
    output = output.lstrip("(")
    output = output.rstrip(")")
    
    n = 0
    for element in output.split(", "):
        n += 1

    arr = np.zeros(n)
    for k, element in enumerate(output.split(", ")):
        arr[k] = dtype(element)

    return arr
    
arr = read_array_variable("y")
print(arr[:10])

    
#print(gdbmi.write("-exec-run ./test/simple"))
