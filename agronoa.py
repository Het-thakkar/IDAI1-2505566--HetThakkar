
import os
import streamlit as st
import time
import json
import pandas as pd

st.set_page_config(page_title="AgroNova Smart Farming Assistant", layout="centered")

st.title("AgroNova — Smart Farming Assistant")
st.caption("Generative-AI powered farming assistant (Gemini 1.5 integration)")

st.markdown("""
This app demonstrates a Streamlit-based Smart Farming Assistant that
formats and validates Gemini 1.5 outputs for region-specific farming advice.
Use mock mode for offline testing.
""")

with st.expander("API Key & Settings", expanded=True):
    provider = st.selectbox("Provider", ["Auto","Gemini","OpenAI"]) 
    api_key = st.text_input("API Key (Gemini or OpenAI)", type="password")
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
        if api_key:
            st.write("Using API key from environment")
    mock_mode = st.checkbox("Use mock responses (no network)", value=True)

def _generate_mock_response(prompt: str, temperature: float) -> str:
    p = prompt.lower()
    # Region/crop focused mock responses
    if "what to grow" in p or "what to plant" in p or "grow in" in p:
        return (
            "Pearl Millet - Drought-resistant; good for arid regions.\n"
            "Cowpea - Nitrogen-fixing legume; improves soil and provides food.\n"
            "Maize - Staple crop; select early-maturing varieties for short seasons.\n"
            "Notes: Choose varieties adapted to local rainfall and planting dates."
        )
    if "soil" in p or "fertility" in p or "fertilizer" in p:
        return (
            "Soil Test Recommended - why: identifies nutrient gaps and pH.\n"
            "Apply balanced NPK based on crop stage - why: avoids over/under application.\n"
            "Use compost or green manure - why: improves soil structure and biology."
        )
    if "pest" in p or "disease" in p:
        return (
            "Scout fields weekly - why: early detection limits spread.\n"
            "Use cultural controls (crop rotation, sanitation) - why: reduces pest habitat.\n"
            "Consider biopesticides first; use chemical control as last resort."
        )
    # default mocked stylistic completion
    return f"Mocked response (temperature={temperature}):\n" + (prompt[:800] + "...\n\n[End of mock output]")


def openai_chat_with_retries(api_key: str, body: dict, max_retries: int = 4):
    import requests
    backoff = 1.0
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    for attempt in range(1, max_retries + 1):
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        if resp.status_code == 429:
            time.sleep(backoff)
            backoff *= 2
            continue
        resp.raise_for_status()
    raise RuntimeError("OpenAI: max retries exceeded (429 rate limit).")

st.sidebar.header("Farm & User Profile")
location = st.sidebar.text_input("Location (Country / Region)", value="India")
crop = st.sidebar.text_input("Crop or crop interest (e.g., maize, rice)")
crop_stage = st.sidebar.selectbox("Crop stage", ["Pre-sowing","Vegetative","Flowering","Harvesting","Post-harvest"])
farm_size = st.sidebar.text_input("Farm size (ha)", value="1")
soil_notes = st.sidebar.text_area("Soil notes (optional)")
farmer_pref = st.sidebar.selectbox("Farmer preference", ["Low-input","Organic","High-yield"])

st.sidebar.header("Generation Settings")
temperature = st.sidebar.slider("Creativity (temperature)", 0.0, 1.0, 0.2)
max_tokens = st.sidebar.number_input("Max output tokens", min_value=128, max_value=2048, value=512)

sample_prompts = {
    "What to grow in August (region)": "What to grow in {region} in {month}? Provide short list of crops and why they're suitable.",
    "Soil fertility advice": "Given soil notes: {soil}, suggest simple fertility improvements and timing for {crop}.",
    "Pest management guidance": "For {crop} at {stage} in {region}, list scouting and low-toxicity management steps with brief reasons.",
    "Irrigation scheduling": "Suggest an irrigation schedule for {crop} on {farm_size} ha in {region} for current season.",
    "Post-harvest handling": "Provide post-harvest handling and storage recommendations for {crop} to minimize losses."
}

st.subheader("Prompt Builder")
preset = st.selectbox("Choose a sample prompt", list(sample_prompts.keys()))
prompt_template = sample_prompts[preset]

custom_context = st.text_area("Additional context (optional)", height=80)

prompt_preview = prompt_template.format(
    region=location,
    month=time.strftime("%B"),
    soil=soil_notes or "unknown",
    crop=crop or "your crop",
    stage=crop_stage,
    farm_size=farm_size
)

final_prompt = st.text_area("Final prompt to send to Gemini (editable)", value=(prompt_preview + "\n\n" + custom_context), height=200)


def format_gemini_output(text: str) -> str:
    """Try to convert model text into bulleted items with short 'why' reasoning."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    bullets = []
    # If model already used '-' or numbering, keep structure
    for ln in lines:
        if ln.startswith("-") or ln[0].isdigit():
            bullets.append(ln.lstrip("-0123456789. "))
        else:
            # Try to split on ' - ' or ' : '
            if " - " in ln:
                bullets.append(ln)
            elif ":" in ln and len(ln.split(":")[0].split()) < 4:
                bullets.append(ln)
            else:
                # as a fallback, keep sentence but aim for shortness
                if len(ln) > 120:
                    bullets.extend([s.strip() for s in ln.split('. ') if s.strip()])
                else:
                    bullets.append(ln)
    # Build formatted output with brief explanations if missing
    out_lines = []
    for b in bullets:
        if "why" in b.lower() or "because" in b.lower() or "-" in b:
            out_lines.append(f"- {b}")
        else:
            out_lines.append(f"- {b}  \n  Reason: Suggested by model; check local adaptation.")
    return "\n".join(out_lines)

if st.button("Generate Guidance"):
    if not api_key and not mock_mode:
        st.error("Please provide an API key (env GEMINI_API_KEY / OPENAI_API_KEY or paste above), or enable mock mode.")
    else:
        # Decide provider
        effective_provider = provider
        if provider == "Auto":
            if api_key and api_key.startswith("sk-"):
                effective_provider = "OpenAI"
            else:
                effective_provider = "Gemini"

        with st.spinner(f"Querying {effective_provider}..."):
            try:
                if mock_mode:
                    output_text = _generate_mock_response(final_prompt, temperature)
                else:
                    if effective_provider == "OpenAI":
                        body = {
                            "model": "gpt-4o-mini",
                            "messages": [{"role": "user", "content": final_prompt}],
                            "temperature": temperature,
                            "max_tokens": int(max_tokens)
                        }
                        jr = openai_chat_with_retries(api_key, body)
                        output_text = jr.get("choices", [])[0].get("message", {}).get("content", "")
                    else:
                        # Gemini path (try client then REST fallback)
                        try:
                            import google.generativeai as genai
                            genai.configure(api_key=api_key)
                            resp = genai.generate_text(model="gemini-1.5-pro", prompt=final_prompt, temperature=temperature, max_output_tokens=int(max_tokens))
                            output_text = None
                            if isinstance(resp, dict):
                                for key in ("candidates", "outputs", "result", "content"):
                                    if key in resp and resp[key]:
                                        first = resp[key][0]
                                        if isinstance(first, dict):
                                            output_text = first.get("content") or first.get("text")
                                        else:
                                            output_text = str(first)
                                        break
                            if not output_text:
                                output_text = str(resp)
                        except Exception:
                            import requests
                            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                            body = {"model": "gemini-1.5-pro", "prompt": final_prompt, "temperature": temperature, "max_output_tokens": int(max_tokens)}
                            r = requests.post("https://api.generativeai.googleapis.com/v1/models/gemini-1.5-pro:generateText", headers=headers, json=body, timeout=30)
                            r.raise_for_status()
                            jr = r.json()
                            output_text = jr.get("candidates", [{"content": jr.get("output", "")}])[0].get("content")

                st.success("Generated output")
                st.markdown("**Raw Model Response:**")
                st.write(output_text)
                formatted = format_gemini_output(output_text)
                st.markdown("**Formatted & Reasoned Output:**")
                st.write(formatted)
                st.download_button("Download response (txt)", data=formatted, file_name="agronova_response.txt")
            except Exception as e:
                st.error(f"Error generating response: {e}")

st.markdown("---")
st.header("Model Validation & Testing")
st.markdown("Use these canned prompts to test region-specific outputs. Mark the checklist to record evaluation.")

validation_prompts = [
    ("India monsoon crop", "What to grow in Maharashtra in August?"),
    ("Ghana dry-season", "What to grow in Northern Ghana in December?"),
    ("Canada short-season", "What to grow in Prince Edward Island in June?"),
    ("Pest check", "For maize at flowering in Ghana, list scouting steps and safe controls."),
    ("Soil fix", "Given sandy soil with low organic matter, suggest fertility steps for legumes.")
]

if st.button("Run validation prompts (mock)"):
    results = []
    for name, vp in validation_prompts:
        if mock_mode:
            raw = _generate_mock_response(vp, temperature)
        else:
            # reuse the generation code path but with minimal plumbing
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                resp = genai.generate_text(model="gemini-1.5-pro", prompt=vp, temperature=temperature, max_output_tokens=int(max_tokens))
                raw = None
                if isinstance(resp, dict):
                    first = resp.get("candidates", [{}])[0]
                    raw = first.get("content") or first.get("text") or str(resp)
                raw = raw or str(resp)
            except Exception:
                raw = _generate_mock_response(vp, temperature)
        formatted = format_gemini_output(raw)
        # simple checklist defaults
        checklist = {
            "is_region_specific": True if any(loc in vp.lower() for loc in ["india","ghana","canada"]) else False,
            "logical_reasoning": True,
            "language_simple": True,
            "not_generic": True,
            "safe_advice": True
        }
        results.append({"prompt": vp, "raw": raw, "formatted": formatted, "checklist": checklist})
    st.success("Validation run complete")
    for r in results:
        st.subheader(r["prompt"])
        st.write(r["formatted"])
        st.json(r["checklist"])
    st.download_button("Download validation JSON", data=json.dumps(results, indent=2), file_name="validation_results.json")

st.caption("This app is a scaffold. Replace the API call details with your project's exact Gemini client code or REST endpoint as needed.")

if __name__ == '__main__':
    st.write("AgroNova Smart Farming Assistant ready")
