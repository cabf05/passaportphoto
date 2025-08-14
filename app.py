import io
from PIL import Image
import streamlit as st
from rembg import remove, new_session

st.set_page_config(page_title="Background Remover", page_icon="🖼", layout="centered")

st.title("🖼 Background Remover — fundo branco")
st.write("Envie uma imagem e o app remove o fundo e coloca **fundo branco**. Funciona melhor com fotos de pessoas/objetos bem destacados.")

# Cacheia a sessão do modelo para não baixar/recarregar a cada execução
@st.cache_resource(show_spinner=False)
def get_session(model_name: str = "u2netp"):
    # "u2netp" é mais leve e rápido; troque para "u2net" se quiser um pouco mais de qualidade
    return new_session(model_name)

session = get_session("u2netp")

# Opções (na barra lateral)
with st.sidebar:
    st.header("Opções")
    max_side = st.slider("Redimensionar (lado máximo, px)", 256, 4096, 2048, step=128,
                         help="Redimensiona apenas para processamento (acelera e evita estouro de memória).")
    out_format = st.selectbox("Formato de download", ["PNG", "JPG"], index=0)
    keep_transparency = st.checkbox("Manter transparência (sem fundo branco)", value=False,
                                    help="Se marcado, exporta PNG com transparência.")

uploaded_file = st.file_uploader("Escolha uma imagem", type=["png", "jpg", "jpeg", "webp"])

def resize_to_max_side(im: Image.Image, max_side_px: int) -> Image.Image:
    w, h = im.size
    if max(w, h) <= max_side_px:
        return im
    if w >= h:
        new_w = max_side_px
        new_h = int(h * (max_side_px / w))
    else:
        new_h = max_side_px
        new_w = int(w * (max_side_px / h))
    return im.resize((new_w, new_h), Image.LANCZOS)

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGBA")
    st.subheader("Imagem original")
    st.image(image, use_column_width=True)

    with st.spinner("Processando..."):
        # Redimensiona para processamento (opcional para performance)
        proc_img = resize_to_max_side(image, max_side)

        # Remove o fundo usando a sessão cacheada
        output_rgba = remove(proc_img, session=session)  # RGBA com alpha

        if keep_transparency:
            final = output_rgba  # mantém o canal alpha
        else:
            # Compor sobre branco
            white_bg = Image.new("RGBA", output_rgba.size, (255, 255, 255, 255))
            final = Image.alpha_composite(white_bg, output_rgba).convert("RGB")

    st.subheader("Resultado")
    st.image(final, use_column_width=True)

    # Arquivo para download
    buf = io.BytesIO()
    if keep_transparency:
        # Se o usuário quis transparência, forçamos PNG (JPG não tem alpha)
        final.save(buf, format="PNG")
        mime = "image/png"
        fname = "image_no_bg.png"
    else:
        if out_format == "PNG":
            # mesmo sem alpha, PNG preserva mais qualidade para figuras/ícones
            final.save(buf, format="PNG")
            mime = "image/png"
            fname = "image_white_bg.png"
        else:
            # JPG com fundo branco
            final_rgb = final.convert("RGB")
            final_rgb.save(buf, format="JPEG", quality=95)
            mime = "image/jpeg"
            fname = "image_white_bg.jpg"

    st.download_button("📥 Baixar", buf.getvalue(), file_name=fname, mime=mime)

st.markdown("---")
st.caption("Feito com Streamlit + rembg (U^2-Net). Se aparecer erro de dependência, veja as instruções do requirements e runtime abaixo.")
