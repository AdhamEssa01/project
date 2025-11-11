https://huggingface.co/datasets/cnamuangtoun/resume-job-description-fit/tree/main
url for data set

1. **spaCy**
   بعد تثبيتها، لازم تنزل الموديل الإنجليزي:

   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **pdfplumber**
   بيستخدمه الكود الجديد في `app/pdf_utils.py` لاستخراج النصوص من الـ CV بدقة.

3. **sentence-transformers**

---

## ⚙️ التثبيت بعد التحديث

من الترمينال داخل مجلد المشروع:

```bash
pip install -r requirements.txt
```

بعدها:

```bash
python -m spacy download en_core_web_sm
```
