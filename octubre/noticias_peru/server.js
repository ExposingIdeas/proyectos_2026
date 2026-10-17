const express = require('express');
const Parser = require('rss-parser');
const ejs = require('ejs');
const fs = require('fs-extra');
const path = require('path');

const app = express();
const parser = new Parser();
const PORT = 3000;

// Configuración de carpetas
app.use(express.static('public')); // Servir la web estática a los usuarios
app.use(express.urlencoded({ extended: true }));

// Fuentes RSS de política en Perú
const FEEDS = [
  { fuente: 'RPP Noticias', url: 'https://rpp.pe/feed/politica' },
  { fuente: 'Agencia Andina', url: 'https://andina.pe/agencia/rss/politica.aspx' },
  { fuente: 'El Comercio', url: 'https://elcomercio.pe/arc/outboundfeeds/rss/category/politica/?outputType=xml' },
  
  // Puedes agregar más fuentes RSS aquí
];

// Función para obtener noticias y compilar el HTML estático
async function generarWebEstatica() {
  console.log("Recopilando noticias...");
  let todasLasNoticias = [];

  for (const feed of FEEDS) {
    try {
      const data = await parser.parseURL(feed.url);
      const items = data.items.slice(0, 5).map(item => ({
        fuente: feed.fuente,
        titulo: item.title,
        link: item.link,
        resumen: item.contentSnippet ? item.contentSnippet.slice(0, 120) + '...' : '',
        fecha: new Date(item.pubDate).toLocaleDateString('es-PE', { 
          day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' 
        }),
        timestamp: new Date(item.pubDate).getTime()
      }));
      todasLasNoticias = todasLasNoticias.concat(items);
    } catch (error) {
      console.error(`Error leyendo ${feed.fuente}:`, error.message);
    }
  }

  // Ordenar por fecha (las más recientes primero)
  todasLasNoticias.sort((a, b) => b.timestamp - a.timestamp);

  // Renderizar la plantilla EJS a un string HTML
  const templatePath = path.join(__dirname, 'views', 'template.ejs');
  const htmlGenerado = await ejs.renderFile(templatePath, {
    noticias: todasLasNoticias,
    ultimaActualizacion: new Date().toLocaleString('es-PE')
  });

  // Guardar físicamente el archivo en la carpeta 'public'
  await fs.ensureDir(path.join(__dirname, 'public'));
  await fs.writeFile(path.join(__dirname, 'public', 'index.html'), htmlGenerado);
  console.log("¡index.html generado exitosamente!");
}

// ---------------- RUTAS ----------------

// Panel de Administración (Solo para ti)
app.get('/admin', (req, res) => {
  res.send(`
    <html>
      <body style="font-family:sans-serif; text-align:center; padding-top:50px;">
        <h2>Panel de Control - Servidor</h2>
        <form action="/admin/actualizar" method="POST">
          <button style="padding: 10px 20px; font-size: 16px; background: red; color: white; border: none; cursor: pointer; border-radius: 5px;">
            Actualizar Noticias Ahora
          </button>
        </form>
      </body>
    </html>
  `);
});

// Acción del Botón
app.post('/admin/actualizar', async (req, res) => {
  try {
    await generarWebEstatica();
    res.send('<p>Sitio web actualizado correctamente. <a href="/">Ver Web</a> | <a href="/admin">Volver</a></p>');
  } catch (error) {
    res.status(500).send("Error generando el sitio.");
  }
});

// Iniciar servidor
app.listen(PORT, async () => {
  console.log(`Servidor corriendo en http://localhost:${PORT}`);
  console.log(`Panel admin en http://localhost:${PORT}/admin`);
  
  // Si no existe el index.html al iniciar, lo creamos
  if (!fs.existsSync(path.join(__dirname, 'public', 'index.html'))) {
    await generarWebEstatica();
  }
});