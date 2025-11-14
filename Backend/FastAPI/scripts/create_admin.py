"""
Script para crear un usuario administrador en la base de datos.
Ejecutar con: python scripts/create_admin.py
"""

import sys
from pathlib import Path

# Agregar el directorio padre al path para importar módulos
sys.path.append(str(Path(__file__).parent.parent))

from db.client import db_client
from utils.security import hash_password

def create_admin():
    """Crea un usuario administrador por defecto"""
    
    admin_data = {
        "name": "Admin",
        "surname": "Sistema",
        "email": "admin@clinica.gob.sv",
        "username": "admin",
        "password": hash_password("admin123")  # CAMBIAR EN PRODUCCIÓN
    }
    
    # Verificar si ya existe un admin
    existing_admin = db_client.Prueba.Admin.find_one({"username": admin_data["username"]})
    
    if existing_admin:
        print(f"⚠️  Ya existe un administrador con el username '{admin_data['username']}'")
        print(f"Email: {existing_admin.get('email')}")
        print(f"Nombre: {existing_admin.get('name')} {existing_admin.get('surname')}")
        return
    
    # Crear el admin
    result = db_client.Prueba.Admin.insert_one(admin_data)
    
    if result.inserted_id:
        print("✅ Administrador creado exitosamente!")
        print(f"\n📋 Credenciales de acceso:")
        print(f"   Usuario: {admin_data['username']}")
        print(f"   Contraseña: admin123")
        print(f"   Email: {admin_data['email']}")
        print(f"\n🔒 IMPORTANTE: Cambia la contraseña después del primer inicio de sesión")
        print(f"\n🌐 Accede en: http://localhost:8000/admin/login")
    else:
        print("❌ Error al crear el administrador")

if __name__ == "__main__":
    create_admin()
