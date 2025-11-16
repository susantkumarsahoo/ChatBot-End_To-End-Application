"""
Create all necessary __init__.py files for Python packages

Run this script to create all __init__.py files:
python create_init_files.py
"""

import os

# Define all directories that need __init__.py
directories = [
    "frontend",
    "frontend/components",
    "backend",
    "backend/routes",
    "backend/models",
    "logic",
    "config",
    "database",
]

# Content for each __init__.py
init_contents = {
    "frontend": '"""Frontend package"""',
    "frontend/components": '"""Frontend components"""',
    "backend": '"""Backend API package"""',
    "backend/routes": '"""API routes package"""',
    "backend/models": '"""Data models package"""',
    "logic": '"""LangChain logic package"""',
    "config": '"""Configuration package"""',
    "database": '"""Database package"""',
}

def create_init_files():
    """Create all __init__.py files"""
    for directory in directories:
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Create __init__.py
        init_file = os.path.join(directory, "__init__.py")
        content = init_contents.get(directory, '"""Package"""')
        
        with open(init_file, 'w') as f:
            f.write(content + '\n')
        
        print(f"✅ Created {init_file}")
    
    print("\n🎉 All __init__.py files created successfully!")

if __name__ == "__main__":
    create_init_files()


# ============================================
# Individual __init__.py file contents:
# ============================================

# frontend/__init__.py
"""Frontend package"""

# frontend/components/__init__.py
"""Frontend components"""

# backend/__init__.py
"""Backend API package"""

# backend/routes/__init__.py
"""API routes package"""

# backend/models/__init__.py
"""Data models package"""

# logic/__init__.py
"""LangChain logic package"""

# config/__init__.py
"""Configuration package"""

# database/__init__.py
"""Database package"""