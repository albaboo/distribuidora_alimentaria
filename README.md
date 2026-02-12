# Distribuidora Alimentaria

📦 Sistema de gestión para una distribuidora de productos alimentarios desarrollado con **Django** siguiendo el patrón arquitectónico **MVT (Model‑View‑Template)**. Permite gestionar productos, categorías, clientes, almacenes, stock, albaranes, preparación de pedidos, estadísticas de ventas e integración con autenticación de Django.

---

## 🧠 Descripción

Esta aplicación web está diseñada para simplificar y automatizar la gestión operativa de una **distribuidora de alimentos**, incluyendo funciones clave como:

- Gestión de **productos** y **categorías**.
- Registro y administración de **clientes**.
- Control de **almacenes** y **stock**.
- Creación y seguimiento de **albaranes** y **pedidos**.
- **Estadísticas de ventas**.
- Autenticación de usuarios con **Django Auth**.

Este proyecto es ideal como base para una solución comercial o como ejercicio académico para aprender a construir aplicaciones completas con Django.

---

## 🚀 Empezando

Sigue estos pasos para ejecutar el proyecto en tu máquina local:

### 📋 Requisitos previos

Antes de comenzar, asegúrate de tener instalados:

- Python (preferiblemente 3.8 o superior)
- Pip
- Virtualenv (opcional pero recomendado)

---

### 🛠️ Instalación y configuración

1. **Clona el repositorio:**

    ```bash
    git clone https://github.com/albaboo/distribuidora_alimentaria.git
    cd distribuidora_alimentaria
    ```

2. **Crea y activa un entorno virtual:**

    ```bash
    python -m venv venv
    source venv/bin/activate    # Linux/Mac
    venv\Scripts\activate       # Windows
    ```

3. **Instala las dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Aplica las migraciones de base de datos:**

    ```bash
    python manage.py migrate
    ```

5. **Crea un superusuario para acceder al panel de administración:**

    ```bash
    python manage.py createsuperuser
    ```

6. **Ejecuta la aplicación:**

    ```bash
    python manage.py runserver
    ```

7. **Abre tu navegador y visita:**

    ```
    http://127.0.0.1:8000/
    ```

---

## 📦 Funcionalidades principales

✨ Incluye:

- CRUD de productos y categorías  
- Gestión de clientes  
- Control de almacenes y stock  
- Gestión de pedidos y albaranes  
- Panel de estadísticas de ventas  
- Acceso restringido por usuario (login/logout)  

---

## 🧪 Pruebas

Si el proyecto tiene pruebas (tests automatizados), agrégalas aquí. Si no, puedes usar Django Admin para probar manualmente las funcionalidades.

---

## 🧩 Estructura del proyecto

Dentro del repositorio verás carpetas como:

```
mini_distribuidora/
mp_app/
templates/
manage.py
db.sqlite3
```

Estas contienen el código de la aplicación principal, plantillas HTML y la base de datos SQLite por defecto.

---

## 🤝 Contribuir

Si deseas colaborar con este proyecto:

1. Haz un fork del repositorio.
2. Crea una rama nueva (`git checkout -b feature/mi‑mejora`).
3. Realiza tus cambios y haz commit (`git commit -m "Descripción de la mejora"`).
4. Haz push a tu rama (`git push origin feature/mi‑mejora`).
5. Abre un Pull Request describiendo tus cambios.

---

## 🛟 Soporte

Si encuentras errores o tienes dudas, abre un *issue* en este repositorio y trataré de ayudarte.

---

## 📄 Licencia

Este proyecto está bajo la licencia **MIT** (si aplica; ajusta si usas otra). Si no tienes un archivo `LICENSE`, puedes añadir uno o quitar esta sección.

---


