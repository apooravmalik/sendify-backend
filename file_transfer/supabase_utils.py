from supabase import create_client
from django.conf import settings
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(os.path.join(__file__, ".."))))

def get_supabase_client():
    SUPABASE_URL = settings.SUPABASE_URL
    SUPABASE_KEY = settings.SUPABASE_KEY
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_file(file, code):
    supabase = get_supabase_client()
    bucket = settings.SUPABASE_BUCKET_NAME

    file_ext = file.name.split('.')[-1]
    file_path = f"{code}.{file_ext}"

    try:
        supabase.storage.from_(bucket).upload(file_path, file, {
            "content-type": file.content_type
        })
        return file_path
    except Exception as e:
        print("Upload failed:", e)
        return None

def get_download_url(code):
    supabase = get_supabase_client()
    bucket = settings.SUPABASE_BUCKET_NAME

    for ext in ['pdf', 'png', 'jpg', 'jpeg', 'txt']:
        file_path = f"{code}.{ext}"
        url = supabase.storage.from_(bucket).get_public_url(file_path)
        if url and 'supabase' in url:
            return url, ext
    return None, None

def delete_file(code, extension):
    supabase = get_supabase_client()
    bucket = settings.SUPABASE_BUCKET_NAME

    file_path = f"{code}.{extension}"
    try:
        supabase.storage.from_(bucket).remove([file_path])
        return True
    except Exception as e:
        print("Deletion failed:", e)
        return False

# TEST BLOCK
if __name__ == "__main__":
    import os
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_settings.settings")
    django.setup()

    from django.conf import settings
    supabase = get_supabase_client()
    bucket = settings.SUPABASE_BUCKET_NAME

    print("✅ Supabase URL:", settings.SUPABASE_URL)

    try:
        files = supabase.storage.from_(bucket).list()
        print("📦 Files in bucket:", files)
    except Exception as e:
        print("❌ Supabase error:", e)
