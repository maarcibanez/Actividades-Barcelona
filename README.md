/* ── Ficha de diseño ──────────────────────────────────────────────
   Inspirado en el trencadís (el mosaico de piezas de cerámica de los
   parques y fachadas modernistas de Barcelona): pequeñas piezas de
   color sobre un fondo neutro. Es la única licencia decorativa de la
   página; el resto es deliberadamente tranquilo y muy legible.

   Paleta:
   #23303D  tinta          texto principal
   #F5F1E8  yeso claro     fondo
   #1D4E89  azul mosaico   cabecera, títulos, marca
   #E3A62F  oro mosaico    acento principal
   #2C6E63  verde mosaico  enlaces / botones
   #B2472B  teja mosaico   acento puntual (solo en la banda y teselas)

   Tipo:
   Segoe UI — familia única para todo (titulares y cuerpo), con una
   cadena de respaldo sobria por si el dispositivo no la tiene
   instalada (no viene de serie en Android/iPhone, solo en Windows).
   ────────────────────────────────────────────────────────────── */

* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }

body {
  margin: 0;
  background: #F5F1E8;
  color: #23303D;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, Arial, sans-serif;
  font-size: 20px;
  line-height: 1.65;
}

a { color: #2C6E63; }

/* ── Cabecera con banda de mosaico ── */

.mosaico {
  height: 14px;
  background:
    radial-gradient(circle at 10% 50%, #E3A62F 0 5px, transparent 5px),
    radial-gradient(circle at 30% 50%, #B2472B 0 5px, transparent 5px),
    radial-gradient(circle at 50% 50%, #F5F1E8 0 5px, transparent 5px),
    radial-gradient(circle at 70% 50%, #2C6E63 0 5px, transparent 5px),
    radial-gradient(circle at 90% 50%, #E3A62F 0 5px, transparent 5px);
  background-size: 60px 14px;
  background-color: #1D4E89;
}

header {
  background: #1D4E89;
  color: #F5F1E8;
  padding: 30px 20px 34px;
  text-align: center;
}

header h1 {
  font-weight: 700;
  font-size: clamp(1.8rem, 6vw, 2.4rem);
  margin: 0 0 10px;
  letter-spacing: 0.2px;
}

header .subtitulo {
  margin: 0;
  font-size: 1.05rem;
  color: #CBDCEE;
}

main {
  max-width: 700px;
  margin: 0 auto;
  padding: 30px 20px 60px;
}

.aviso {
  background: #FCEFD4;
  border: 2px solid #E3A62F;
  border-radius: 4px;
  padding: 16px 18px;
  font-size: 1rem;
  margin-bottom: 30px;
}

.sin-eventos {
  font-size: 1.15rem;
  text-align: center;
  padding: 50px 10px;
  color: #4c5866;
}

/* ── Días ── */

.dia { margin-bottom: 44px; }

.dia h2 {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 1.4rem;
  color: #1D4E89;
  margin: 0 0 20px;
  text-transform: capitalize;
}

.dia h2::before {
  content: "";
  display: inline-block;
  width: 14px;
  height: 14px;
  background: #E3A62F;
  border-radius: 3px;
  transform: rotate(45deg);
  flex: none;
}

/* ── Tarjeta de evento, con "tesela" de color en el lateral ── */

.evento {
  position: relative;
  background: #FFFFFF;
  border-radius: 10px;
  padding: 20px 22px 20px 26px;
  margin-bottom: 18px;
  box-shadow: 0 2px 8px rgba(29, 78, 137, 0.08);
  overflow: hidden;
}

.evento::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 8px;
  height: 100%;
  background: linear-gradient(180deg, #E3A62F, #B2472B);
}

.evento h3 {
  font-weight: 700;
  margin: 0 0 10px;
  font-size: 1.3rem;
  color: #1D4E89;
}

.evento .lugar {
  margin: 0 0 10px;
  font-weight: 700;
}

.evento .hora {
  font-weight: 400;
  color: #5a6472;
}

.evento .descripcion {
  margin: 0 0 14px;
  color: #3a4552;
}

.evento .mas-info {
  display: inline-block;
  font-size: 1.02rem;
  font-weight: 700;
  color: #FFFFFF;
  background: #2C6E63;
  padding: 11px 20px;
  border-radius: 8px;
  text-decoration: none;
}

.evento .mas-info:focus,
.evento .mas-info:hover {
  outline: 3px solid #E3A62F;
  outline-offset: 2px;
}

footer {
  text-align: center;
  padding: 24px 20px;
  color: #6b7480;
  font-size: 0.95rem;
}

@media (max-width: 480px) {
  body { font-size: 19px; }
}
