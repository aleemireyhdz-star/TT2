# 🌐 Guía de Instalación - Cloudflare Tunnel

## ¿Qué es Cloudflare Tunnel?

Cloudflare Tunnel permite exponer tu servidor local a internet de forma segura sin necesidad de:
- Cambiar configuración del router
- Abrir puertos
- Obtener una IP estática
- Usar VPNs complicadas

La URL será **permanente y segura**.

---

## 📋 Paso 1: Crear cuenta en Cloudflare

1. Ve a https://dash.cloudflare.com
2. Crea una cuenta gratuita con tu email
3. Completa la verificación

---

## 📥 Paso 2: Instalar Cloudflare CLI (cloudflared)

### En Windows

Descarga el instalador desde:
https://github.com/cloudflare/cloudflare-warp/releases

O usa Chocolatey:
```powershell
choco install cloudflare-warp
```

O descargalo manualmente y colócalo en una carpeta del PATH.

**Verifica la instalación:**
```powershell
cloudflared --version
```

---

## 🔐 Paso 3: Autenticar cloudflared

Ejecuta:
```powershell
cloudflared login
```

Esto abrirá tu navegador. Selecciona tu dominio o crea uno gratuito en Cloudflare.

Después de autorizar, se guardará un certificado en:
```
C:\Users\<tuusuario>\.cloudflared\cert.pem
```

---

## 🚀 Paso 4: Crear el Túnel

### Opción A: Con un dominio de Cloudflare (Recomendado)

1. **Crear el túnel:**
```powershell
cloudflared tunnel create sistema-inundaciones
```

Esto creará el túnel y mostrará un UUID. Anótalo.

2. **Crear archivo de configuración:**

Crea un archivo `~\.cloudflared\config.yml` con:

```yaml
tunnel: sistema-inundaciones
credentials-file: C:\Users\<tuusuario>\.cloudflared\<UUID>.json

ingress:
  - hostname: sistema-inundaciones.midominio.com
    service: http://localhost:5000
  - service: http_status:404
```

(Reemplaza `<tuusuario>` y `<UUID>` con tus valores)

3. **Crear registro DNS:**
```powershell
cloudflared tunnel route dns sistema-inundaciones sistema-inundaciones.midominio.com
```

4. **Iniciar el túnel:**
```powershell
cloudflared tunnel run sistema-inundaciones
```

---

### Opción B: Sin dominio (Usando one-time URL)

```powershell
cloudflared tunnel run --url http://localhost:5000
```

Esto generará una URL aleatoria que expirará en 30 minutos.

---

## ✅ Paso 5: Iniciar la aplicación

En **otra terminal**, navega a tu proyecto y ejecuta:

```powershell
cd 'c:\Users\sergi\OneDrive - Instituto Politecnico Nacional\Documents\UPIITA\9no. semestre\TT\VSCode\TT2\src'
python Flask_Server.py
```

---

## 🌐 Paso 6: Acceder a tu aplicación

Ahora accede desde cualquier lugar:
- **Con dominio:** `https://sistema-inundaciones.midominio.com`
- **Sin dominio:** La URL mostrada por cloudflared en la terminal

---

## 📊 Comandos útiles

### Ver estado de los túneles
```powershell
cloudflared tunnel list
```

### Ver detalles del túnel
```powershell
cloudflared tunnel info sistema-inundaciones
```

### Eliminar un túnel
```powershell
cloudflared tunnel delete sistema-inundaciones
```

### Ver logs en tiempo real
```powershell
cloudflared tunnel logs sistema-inundaciones
```

---

## 🔒 Seguridad

- La conexión es **encriptada HTTPS**
- Cloudflare actúa como proxy (oculta tu IP real)
- Puedes agregar autenticación de Cloudflare Access si lo necesitas

---

## 🛠️ Troubleshooting

### "cloudflared not found"
- Asegúrate de haber instalado cloudflared correctamente
- Reinicia PowerShell después de instalar

### "tunnel already running"
- Ejecuta `cloudflared tunnel kill` en otra terminal
- O encuentra el proceso: `Get-Process cloudflared`

### "Conexión rechazada"
- Verifica que Flask esté corriendo en otra terminal
- Verifica que el puerto sea 5000
- Revisa el archivo `config.yml`

---

## 📱 Compartir la URL

Una vez que todo esté corriendo, puedes compartir la URL con:
- **Equipo:** Acceso desde cualquier dispositivo
- **Móviles:** Funciona perfectamente
- **Público:** Seguro y permanente

---

## ⚙️ Automatizar (Opcional)

Para que el túnel se inicie automáticamente al encender la PC:

1. Instala como servicio:
```powershell
cloudflared service install
```

2. Inicia el servicio:
```powershell
Start-Service cloudflared
```

---

**¿Necesitas ayuda?** Revisa la documentación oficial:
https://developers.cloudflare.com/cloudflare-one/connections/connect-applications/install-and-setup/

---

Creado: Diciembre 2025
Proyecto: Sistema de Alertas de Inundaciones CDMX
