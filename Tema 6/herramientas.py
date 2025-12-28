from langchain_core.tools import Tool
from langchain_experimental.utilities import PythonREPL

python_repl = PythonREPL()

tool = Tool(
    name="Python_repl",
    func=python_repl.run,
    description="Ejecuta codigo en Python en un interprete para calculos o logica matematica."
)

output = tool.run("print(2+2)")
print(output)