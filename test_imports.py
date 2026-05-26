import sys
print("Python version:", sys.version)
print()

modules = ['flask', 'docx', 'openai', 'dotenv']
for module_name in modules:
    try:
        module = __import__(module_name)
        print(f"✓ {module_name} imported successfully")
        # Try to get version if available
        if hasattr(module, '__version__'):
            print(f"  Version: {module.__version__}")
    except ImportError as e:
        print(f"✗ Failed to import {module_name}: {e}")
    except Exception as e:
        print(f"✗ Error importing {module_name}: {e}")