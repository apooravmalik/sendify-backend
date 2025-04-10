from django.http import JsonResponse, FileResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .supabase_utils import get_supabase_client
from .code_utils import generate_code
import mimetypes
from django.http import HttpResponse

MAX_FILE_SIZE_MB = 10

@csrf_exempt
def upload_file(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Only POST allowed.")
    
    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return HttpResponseBadRequest("No file uploaded.")
    
    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return HttpResponseBadRequest("File exceeds 10MB limit.")
    
    # Generate short unique code
    code = generate_code()
    file_path = f"{code}_{uploaded_file.name}"

    # Read file content as bytes
    file_content = uploaded_file.read()
    
    supabase = get_supabase_client()
    bucket = settings.SUPABASE_BUCKET_NAME

    # Upload to Supabase (note: pass bytes instead of file object)
    supabase.storage.from_(bucket).upload(file_path, file_content, {
        "content-type": uploaded_file.content_type
    })

    return JsonResponse({"code": code})


@csrf_exempt
def download_file(request):
    if request.method == "POST":
        code = request.POST.get("code", "").strip()
        supabase = get_supabase_client()
        bucket = settings.SUPABASE_BUCKET_NAME

        all_files = supabase.storage.from_(bucket).list()
        matching_file = next((f["name"] for f in all_files if f["name"].startswith(code + "_")), None)

        if not matching_file:
            return JsonResponse({"error": "File not found"}, status=404)

        response = supabase.storage.from_(bucket).download(matching_file)
        file_bytes = response

        filename = matching_file.split("_", 1)[1]
        mime_type, _ = mimetypes.guess_type(filename)
        response = HttpResponse(file_bytes, content_type=mime_type or 'application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        # Optional: delete the file after download
        supabase.storage.from_(bucket).remove(matching_file)

        return response