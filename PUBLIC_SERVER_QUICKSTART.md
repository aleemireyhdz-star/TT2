# 🌐 Hacer tu Aplicación Pública - Guía Rápida

## ⚡ Opción Elegida: Cloudflare Tunnel (Estable & Permanente)

### ✅ Ventajas
- ✨ URL permanente y segura
- 🔒 Encriptación HTTPS automática
- 🌍 Accesible desde cualquier lugar
- 🆓 Gratuito para siempre
- 🚀 Sin necesidad de cambiar router/puertos

---

## 🚀 Inicio Rápido (3 pasos)

### 1️⃣ Instalar Cloudflare CLI

```powershell
# Opción A: Con Chocolatey
choco install cloudflare-warp

# Opción B: Descarga manual
# https://github.com/cloudflare/cloudflare-warp/releases
```

**Verifica la instalación:**
```powershell
cloudflared --version
```

### 2️⃣ Crear y configurar el túnel

```powershell
# Autenticar
cloudflared login

# Crear el túnel
cloudflared tunnel create sistema-inundaciones

# Configurar DNS (si tienes dominio de Cloudflare)
cloudflared tunnel route dns sistema-inundaciones sistema-inundaciones.midominio.com
```

> 📝 Nota: Si no tienes dominio, puedes usar la URL aleatoria que genera cloudflared

### 3️⃣ Iniciar todo

**Opción A: Script PowerShell (Recomendado)**
```powershell
# Habilitar ejecución de scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Ejecutar
.\Start-PublicServer.ps1
```

**Opción B: Dos terminales**
```powershell
# Terminal 1: Flask
cd src
python Flask_Server.py

# Terminal 2: Cloudflare Tunnel
cloudflared tunnel run sistema-inundaciones
```

---

## 🌐 Acceder a tu aplicación

Una vez que todo esté corriendo:

```
https://sistema-inundaciones.midominio.com
```

O la URL mostrada por cloudflared si no tienes dominio.

---

## 📖 Documentación Completa

Para más detalles, consulta: `CLOUDFLARE_SETUP.md`

---

## 🔧 Troubleshooting

**"cloudflared not found"**
```powershell
# Verifica la instalación
Get-Command cloudflared

# Si no funciona, descárgalo manualmente
```

**"Port 5000 already in use"**
```powershell
# Encuentra el proceso
Get-Process | Where-Object { $_.Name -like "*python*" }

# Termínalo
Stop-Process -Name "python" -Force
```

**"Tunnel creation failed"**
```powershell
# Verifica que estés autenticado
cloudflared tunnel login

# Lista tus túneles
cloudflared tunnel list
```

---

## 📊 Comandos útiles

```powershell
# Ver todos los túneles
cloudflared tunnel list

# Ver logs en tiempo real
cloudflared tunnel logs sistema-inundaciones

# Eliminar un túnel
cloudflared tunnel delete sistema-inundaciones

# Cambiar el puerto (si necesitas)
# Edita la configuración en: ~/.cloudflared/config.yml
```

---

## 🎯 Próximos pasos

1. ✅ Instala cloudflared
2. ✅ Crea el túnel
3. ✅ Inicia con el script PowerShell
4. ✅ Comparte la URL con tu equipo
5. ✅ ¡Disfruta tu aplicación pública!

---

**¿Necesitas ayuda?**
- 📚 Docs oficiales: https://developers.cloudflare.com/cloudflare-one/connections/connect-applications/
- 💬 Comunidad: https://community.cloudflare.com/

Creado: Diciembre 2025
