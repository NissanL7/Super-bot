import aiohttp
import os

@app_commands.command(name="chat", description="Chat with AI")
@app_commands.describe(prompt="Your question")
async def chat(self, interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    
    # Format prompt for Mistral
    formatted_prompt = f"<s>[INST] {prompt} [/INST]"
    payload = {
        "inputs": formatted_prompt,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.7,
            "return_full_text": False
        }
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    ai_reply = result[0]['generated_text'].strip()
                    
                    embed = discord.Embed(
                        title="🧠 AI Response", 
                        description=ai_reply[:4000] if ai_reply else "No response generated",
                        color=0x9b59b6
                    )
                    embed.set_footer(text="Powered by Hugging Face - Mistral 7B")
                    await interaction.followup.send(embed=embed)
                else:
                    error_text = await resp.text()
                    await interaction.followup.send(f"❌ API Error: {resp.status}\n{error_text[:200]}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
