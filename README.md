IFC Merge Utility

A simple command-line tool for merging multiple IFC files into one, with basic support for preserving element colors.
🧩 What is this?

When working in Revit, it's common to use linked models. However, when exporting to IFC, each link is saved as a separate IFC file. Most IFC viewers don’t support loading these files as a unified model. Typically, users must either:

    Use complex software to merge files,

    Or bind all links inside Revit before export — which is not always convenient.

This tool solves that. If you have Python installed and the ifcopenshell library, you can quickly merge IFC files from the command line.
✅ Features

    Merges multiple .ifc files into one

    Keeps the element colors from the base file (as much as possible)

    Supports material/style/styled item merging

    Minimal setup, no GUI, no Revit needed

🔧 Requirements

    Python 3.6+

    ifcopenshell library
    Install via:

pip install ifcopenshell

🚀 How to Use

python mergeifc.py output.ifc base.ifc linked1.ifc linked2.ifc ...

    output.ifc: The result file.

    base.ifc: Your main model. Its colors and styles have priority.

    linkedX.ifc: Additional files to merge in.

⚠️ All files must share the same insertion point (i.e., same coordinates), otherwise the models won’t align properly.
🖌️ Color Handling

    The script attempts to preserve materials, surface styles, and styled items.

    Priority is given to the first (base) file.

    Colors from other files are merged if no conflict occurs.

    Resulting color fidelity may vary depending on the source files.

🧪 Extra: Analyze a file

You can inspect a file's material and color info using:

python mergeifc.py --analyze file.ifc

📄 License

MIT License – do whatever you want, but no warranties.

Created by Ivan Rodionov, with AI assistance.
Initial concept and prototype by Google Gemini.
Color and material logic refined with help from Claude by Anthropic.
