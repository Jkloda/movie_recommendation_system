import httpx
import asyncio

class HttpLayer():
    def __init__(self):
        self.transport = httpx.AsyncHTTPTransport(retries=5)
        self.headers = {'Content-Type':'application/json'}
        self.url = 'http://localhost:11434/api/generate'
        

    async def prompt_lama(self, prompt):
        body = {
            'model': 'llama3.2',
            'prompt': f'ten most similar movies, no additional text, do not repeat movies in prompt, format [title§ description], [title§ description], given the following {prompt}',
            'stream': False
        }
        try:
            timeout = httpx.Timeout(30.0, connect=30.0)
            async with httpx.AsyncClient(transport=self.transport, timeout=timeout) as client:
                response = await client.post(url=self.url, headers=self.headers, json=body)
                if response.status_code == 200:  
                    return response.json()['response']
                else:
                    return 'error', 400
        except Exception as e:
            return f'error: {e}', 500
            
    async def get_recommendations(self, prompt):
        response = await self.prompt_lama(prompt)
        return response

