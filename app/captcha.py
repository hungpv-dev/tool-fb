import requests
import base64
import time
import logging

class Captcha: 
    def __init__(self):
        from helpers.base import config
        self.token = config('omocaptcha_token')
    
    def getCode(self, url):
        base64Image = self.decodeBase64Img(url)
        print(f'Lấy cap cha từ: {url}')
        if base64Image is None:
            raise ValueError('Không thể decode hình ảnh')
        
        job_id = self.createJob(base64Image)
        print(f'Call api tạo job: {job_id}')
        if job_id is None:
            raise ValueError('Không thể lấy job id')
        
        code = self.getResult(job_id)
        print(f'Lấy code: {code}')
        if code is None:
            raise ValueError('Không thể lấy code')
        
        return code

        

    def decodeBase64Img(self, url):
        res = requests.get(url)
        content = None
        if res.status_code == 200:
            content = base64.b64encode(res.content).decode('utf-8')
        return content
    
    def createJob(self, base64Image):
        api = 'https://omocaptcha.com/api/createJob'
        data = {
            'api_token': self.token,
            'data': {
                'type_job_id': 30,
                'image_base64': base64Image
            }
        }
        res = requests.post(api, json=data)
        res = res.json()
        job_id = None
        if res.get("success"):
            job_id = res.get("job_id")
        return job_id
    
    def getResult(self,job_id):
        code = ''
        while True:
            result = requests.post('https://omocaptcha.com/api/getJobResult', json={
                "api_token": self.token,
                "job_id": job_id
            })
            result = result.json()
            status = result.get('status')
            print(f'Lấy code status: {status}')
            if 'success' in status or 'fail' in status:
                if 'fail' in status:
                    print(result)
                    logging.info(result)
                code = result.get('result')
                break
            time.sleep(2)
        return code

    