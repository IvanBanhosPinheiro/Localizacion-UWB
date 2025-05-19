# 📡 Localización UWB en Talleres con ESP32 + DW1000

Este proyecto permite la localización en tiempo real de vehículos dentro de un taller mediante tecnología UWB (Ultra Wide Band) con ESP32 y DW1000. Utiliza anclas fijas y etiquetas móviles que reportan su distancia a un servidor Flask vía WiFi, el cual calcula la posición de los vehículos y la muestra en un plano interactivo.

---

## 🚀 Tecnologías

- **ESP32 + DW1000**: Hardware de localización basado en UWB.
- **Arduino**: Código para anclas (`anchor.txt`) y etiquetas (`tag.txt`).
- **Flask**: Servidor API para gestionar tags, anchors, vehículos y posiciones.
- **MySQL**: Base de datos relacional para almacenar entidades y posiciones.
- **SVG**: Representación visual del taller y zonas.
- **WiFi**: Comunicación inalámbrica entre dispositivos y servidor.

---

## 📁 Estructura del Repositorio

// Estructura general

- `anchor.ino` → Código Arduino para anclas UWB fijas  
- `tag.ino` → Código Arduino para etiquetas móviles UWB  
- `link.cpp`, `link.h` → Gestión de enlaces UWB y promedio de medidas  
- `script.sql` → Script SQL para crear y poblar la base de datos  
- `Atopcar.postman_collection.json` → Documentación de la API REST del servidor para postman  


---

## ⚙️ Funcionamiento General

1. Las **anclas** (anchors) permanecen fijas en el taller.
2. Los **tags** móviles realizan ranging con los anchors cercanos.
3. Cada x segundos, el tag envía un JSON vía HTTP al servidor con las distancias medidas.
4. El servidor registra las distancias y triangula la posición del tag.
5. La posición se guarda y puede visualizarse sobre un plano SVG del taller.

---

## 🧪 Ejemplo de JSON enviado por un tag

```json
{
  "tag": "T01",
  "links": [
    { "A": "A01", "R": "2.1" },
    { "A": "A02", "R": "1.7" },
    { "A": "A03", "R": "3.4" }
  ]
}
```
---

## 🛠️ Endpoints Destacados

### 📍 Posiciones

- `GET /positions/latest` – Últimas posiciones
- `GET /positions/tag/:tag_id` – Posición de un tag
- `GET /positions/tag/:tag_id/history` – Historial por tag
- `POST /positions` – Registrar posición manualmente

### 🧾 Tags

- `GET /tags` – Listar todos los tags
- `POST /tags` – Registrar nuevo
- `PUT /tags/:id/release` – Liberar tag
- `GET /tags/available` – Ver tags libres

### 🛰️ Anchors

- `GET /anchors` – Listar anclas
- `POST /anchors` – Añadir nueva
- `PUT /anchors/:id` – Editar datos y posición

### 🚗 Vehículos

- `GET /vehicles` – Todos los vehículos
- `POST /vehicles` – Registrar nuevo
- `PUT /vehicles/:id/assign-tag` – Asignar tag a vehículo
- `GET /vehicles/:id/position` – Obtener posición actual

## 📚 Documentación de la API

Todos los endpoints REST están documentados de dos formas:

1. **Postman**  
   En el repositorio encontrarás un archivo JSON con la colección completa de endpoints que puedes importar directamente en Postman para realizar pruebas.

2. **Swagger UI**  
   Si ejecutas el servidor Flask, accede a la documentación navegando a:  
   `http://localhost:5000/apidocs/`  
   Allí encontrarás una descripción interactiva de todos los endpoints disponible con `swagger_ui`.

---
## 🧱 Base de Datos

La estructura de base de datos está definida en `script.txt` e incluye:

- `tags` – Dispositivos móviles
- `anchors` – Anclas fijas
- `vehiculos` – Vehículos en el taller
- `posiciones` – Historial de ubicaciones
- `distancias` – Última medición entre tag y 3 anchors
- `zonas`, `talleres`, `alertas`, etc.

---

## 📌 Código de Tag ESP32-UWB

- Se conecta al WiFi
- Realiza ranging UWB con anchors
- Promedia las distancias con `fresh_link`
- Envía el JSON con `make_link_json` y `send_udp`

Fragmento:

```cpp
make_link_json(uwb_data, &all_json);
send_udp(&all_json);
```

---

## 📌 Código de Anchor ESP32-UWB

- Inicia como receptor UWB
- Detecta dispositivos cercanos
- Informa en serie los datos de distancia y potencia recibida

Fragmento:

```cpp
DW1000Ranging.startAsAnchor(ANCHOR_ADD, DW1000.MODE_LONGDATA_RANGE_LOWPOWER, false);
```

---

## 📐 Cálculo de Posición

El cálculo se realiza por trilateración, usando las distancias medidas a 3 anclas con coordenadas conocidas. Se promedian las últimas 3 medidas para cada ancla para mejorar la estabilidad.

```cpp
temp->range[0] = (range + temp->range[1] + temp->range[2]) / 3;
```

---

## 🧑‍💻 Autores

Este proyecto ha sido desarrollado por:

- [Ivan Baños Piñeiro](https://github.com/IvanBanhosPinheiro)
- [Alba Rodríguez Fernández](https://github.com/albarf1)
- [Iago Malvido Guzmán](https://github.com/Iago-3004)
- [Javier Feijóo López](https://github.com/javier-feijoo)
- [Jorge Sobrino Mojón](https://github.com/Jsobrino98)

---

## ⚖️ Licencia

Este proyecto se distribuye bajo la **Licencia MIT modificada**:  
- Uso libre para proyectos educativos, académicos y de investigación  
- Está prohibida su **venta comercial sin autorización previa**  
- Se debe mantener la autoría en todo uso derivado

---
