import streamlit as st
from rembg import remove
from PIL import Image
import io

# Configuração da página
st.set_page_config(page_title="Background Remover", page_icon="🖼", layout="centered")

# Título
st.title("🖼 Background Remover - White Background")
st.write("Upload an image and this tool will remove the background and replace it with white.")

# Upload da imagem
uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Exibir imagem original
    image = Image.open(uploaded_file).convert("RGBA")
    st.subheader("Original image")
    st.image(image, use_column_width=True)

    with st.spinner("Processing..."):
        # Remover fundo
        output = remove(image)

        # Criar fundo branco
        white_bg = Image.new("RGBA", output.size, (255, 255, 255, 255))
        final_image = Image.alpha_composite(white_bg, output).convert("RGB")

    # Exibir imagem final
    st.subheader("Image with white background")
    st.image(final_image, use_column_width=True)

    # Botão para download
    buf = io.BytesIO()
    final_image.save(buf, format="PNG")
    st.download_button(
        label="📥 Download PNG",
        data=buf.getvalue(),
        file_name="image_white_bg.png",
        mime="image/png"
    )

# Rodapé
st.markdown("---")
st.markdown("Developed with ❤️ using [Streamlit](https://streamlit.io/) and [rembg](https://github.com/danielgatis/rembg)")
