import os
import json
import zipfile
import requests
import gradio as gr

def make_minecraft_addon(user_prompt):
    API_URL = "https://huggingface.co"
    
    system_instruction = (
        "You are an expert Minecraft Bedrock Add-on developer. Create an asset bundle for the user. "
        "Your output must be a single, valid JSON object containing exactly two keys: "
        "'manifest' (the json manifest configuration) and 'logic_js' (the script logic file text). "
        "Do not include any conversational text, pleasantries, or markdown blocks (like ```json)."
    )
    
    payload = {
        "inputs": f"<|system|>\n{system_instruction}\n<|user|>\nCreate an add-on for: {user_prompt}\n<|assistant|>\n",
        "parameters": {"max_new_tokens": 1500, "return_full_text": False}
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        ai_response_text = response.json()['generated_text'].strip()
        
        parsed_data = json.loads(ai_response_text)
        manifest_content = parsed_data.get("manifest", {})
        js_content = parsed_data.get("logic_js", "// No code generated")
        
        manifest_path = "manifest.json"
        js_path = "main.js"
        addon_path = "custom_mod.mcaddon"
        
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest_content, f, indent=4)
            
        with open(js_path, "w", encoding="utf-8") as f:
            f.write(js_content)
            
        with zipfile.ZipFile(addon_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.write(manifest_path)
            zip_file.write(js_path)
            
        os.remove(manifest_path)
        os.remove(js_path)
        
        return addon_path
        
    except Exception as e:
        return f"Error building package: {str(e)}. Try refining your prompt."

interface = gr.Interface(
    fn=make_minecraft_addon,
    inputs=gr.Textbox(label="What block, item, or rule do you want to create?", placeholder="e.g., A ruby pickaxe that mines faster..."),
    outputs=gr.File(label="Download your working .mcaddon file"),
    title="⛏️ Free MC Mod AI Generator",
    description="Type an idea, press submit, and get a downloadable Minecraft Add-on file."
)

if __name__ == "__main__":
    interface.launch(share=True)
