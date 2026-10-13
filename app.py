import base64
import os
from io import BytesIO

import streamlit as st
from google import genai
from PIL import Image


# --------------------------------------------------
# Page configuration
# --------------------------------------------------
st.set_page_config(
    page_title="AI Vision Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# Custom styling
# --------------------------------------------------
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.6rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    .subtitle {
        text-align: center;
        color: #808080;
        margin-bottom: 2rem;
    }
    .stButton button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Secure API key retrieval
# --------------------------------------------------
def get_api_key():
    # Streamlit Community Cloud / local secrets
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
        if key:
            return key
    except Exception:
        pass

    # Environment variable fallback
    return os.getenv("GEMINI_API_KEY", "")


# --------------------------------------------------
# Image generation
# --------------------------------------------------
def generate_image(prompt, api_key, aspect_ratio, image_size):
    client = genai.Client(api_key=api_key)

    response = client.interactions.create(
        model="gemini-3.1-flash-image",
        input=prompt,
        response_format={
            "type": "image",
            "mime_type": "image/png",
            "aspect_ratio": aspect_ratio,
            "image_size": image_size,
        },
    )

    # The API returns the image as base64-encoded data.
    if not getattr(response, "output_image", None):
        raise RuntimeError(
            "The model did not return an image. "
            "Try a more descriptive prompt or check API access."
        )

    image_bytes = base64.b64decode(response.output_image.data)
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    return image


# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown(
    '<div class="main-title">🎨 AI Vision Studio</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="subtitle">'
    'Transform your imagination into images with Gemini AI'
    '</div>',
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Sidebar settings
# --------------------------------------------------
with st.sidebar:
    st.header("⚙️ Image Settings")

    style = st.selectbox(
        "Choose an artistic style",
        [
            "Photorealistic",
            "Digital Art",
            "3D Render",
            "Anime",
            "Watercolor Painting",
            "Pencil Sketch",
            "Cinematic",
            "Minimalist Illustration",
        ],
    )

    aspect_ratio = st.selectbox(
        "Image aspect ratio",
        ["1:1", "16:9", "9:16", "4:3", "3:4"],
        index=0,
    )

    image_size = st.selectbox(
        "Image resolution",
        ["1K", "2K"],
        index=0,
        help="Higher resolutions may use more quota.",
    )

    st.divider()
    st.caption("Powered by Google's Gemini image model.")
    st.caption("API usage may be subject to quotas and charges.")

# --------------------------------------------------
# Prompt input
# --------------------------------------------------
st.subheader("Describe the image you want")

examples = {
    "Smart Hospital": (
        "A futuristic smart hospital with AI-powered robots, "
        "doctors using holographic displays, clean architecture"
    ),
    "Fantasy World": (
        "A magical floating island above the clouds, "
        "glowing waterfalls, fantasy environment"
    ),
    "Eco-Friendly City": (
        "A sustainable green city with solar buildings, "
        "electric transport and rooftop gardens"
    ),
    "Space Exploration": (
        "Astronauts exploring a beautiful alien planet, "
        "distant galaxies and dramatic lighting"
    ),
}

example_choice = st.selectbox(
    "Try an example prompt",
    ["Write my own prompt"] + list(examples.keys()),
)

default_prompt = examples.get(example_choice, "")

prompt = st.text_area(
    "Image description",
    value=default_prompt,
    placeholder=(
        "Example: A tiny robot reading a book in a "
        "sunlit futuristic library, detailed digital art"
    ),
    height=130,
    max_chars=1500,
)

st.caption(
    "Tip: Describe the subject, setting, lighting, colors, "
    "composition, and artistic style."
)

generate = st.button(
    "✨ Generate Image",
    type="primary",
    use_container_width=True,
)

# --------------------------------------------------
# Generate and display
# --------------------------------------------------
if generate:
    if not prompt.strip():
        st.warning("Please enter an image description.")
        st.stop()

    api_key = get_api_key()

    if not api_key:
        st.error(
            "Gemini API key not found. Configure "
            "GEMINI_API_KEY in Colab Secrets for testing, "
            "or in Streamlit Cloud Secrets for deployment."
        )
        st.stop()

    full_prompt = (
        f"Generate one high-quality image in {style} style. "
        f"Subject and scene: {prompt.strip()}. "
        "Create a visually coherent composition with "
        "careful lighting, clear details, and suitable colors. "
        "Avoid unnecessary text and watermarks."
    )

    try:
        with st.spinner(
            "Creating your image with Gemini AI... "
            "This may take a little while."
        ):
            image = generate_image(
                full_prompt,
                api_key,
                aspect_ratio,
                image_size,
            )

        st.success("Your image has been generated!")

        left, right = st.columns([3, 1])

        with left:
            st.image(
                image,
                caption=f"Generated image — {style}",
                use_container_width=True,
            )

        with right:
            st.subheader("Image details")
            st.write(f"**Style:** {style}")
            st.write(f"**Aspect ratio:** {aspect_ratio}")
            st.write(f"**Resolution setting:** {image_size}")
            st.write(f"**Dimensions:** {image.width} × {image.height}")

            buffer = BytesIO()
            image.save(buffer, format="PNG")

            st.download_button(
                label="⬇️ Download PNG",
                data=buffer.getvalue(),
                file_name="ai_generated_image.png",
                mime="image/png",
                use_container_width=True,
            )

        with st.expander("View the complete generation prompt"):
            st.write(full_prompt)

    except Exception as error:
        st.error(
            "Image generation failed. Check your API key, "
            "model availability, quota, billing requirements, "
            "and network connection."
        )
        st.caption(f"Technical details: {str(error)[:700]}")

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()
st.caption(
    "AI Vision Studio | Generative AI Capstone Project"
)
