"""
Certificate Generator for CyberTraining Platform
Generates certificates when users complete all machines
"""
import os
import uuid
from datetime import datetime, timedelta
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont

# Certificate template path - use static image from frontend
TEMPLATE_FILENAME = "cybertraining_certificate.jpg"


def generate_certificate_id():
    """Generate unique certificate ID like CT-2026-001"""
    year = datetime.now().year
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"CT-{year}-{unique_id}"


def create_certificate(name, cert_id, output_path=None):
    """
    Create a certificate image with the user's name and details
    Uses static template from frontend public folder
    
    Args:
        name: User's name to put on certificate
        cert_id: Unique certificate ID
        output_path: Path to save the certificate (optional)
    
    Returns:
        Path to the generated certificate image
    """
    # Try to find template in multiple locations (frontend public folder)
    template_paths = [
        os.path.join(settings.BASE_DIR, '..', 'frontend', 'public', TEMPLATE_FILENAME),
        os.path.join(settings.BASE_DIR, 'frontend', 'public', TEMPLATE_FILENAME),
        os.path.join(settings.MEDIA_ROOT, TEMPLATE_FILENAME),
        os.path.join(settings.BASE_DIR, TEMPLATE_FILENAME),
    ]
    
    template_path = None
    for path in template_paths:
        if os.path.exists(path):
            template_path = path
            break
    
    if template_path is None:
        # Create a basic certificate if template not found
        img = Image.new('RGB', (1000, 700), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add border
        draw.rectangle([(10, 10), (990, 690)], outline='gold', width=5)
        draw.rectangle([(20, 20), (980, 680)], outline='darkblue', width=2)
    else:
        img = Image.open(template_path)
        draw = ImageDraw.Draw(img)
    
    # Fonts - use default if arial not available
    try:
        name_font = ImageFont.truetype("arial.ttf", 60)
        text_font = ImageFont.truetype("arial.ttf", 35)
    except:
        name_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    width, height = img.size
    
    # -------- USER NAME --------
    # Center the name
    name_bbox = draw.textbbox((0, 0), name, font=name_font)
    name_width = name_bbox[2] - name_bbox[0]
    name_position = ((width - name_width) // 2, height // 2 - 50)
    draw.text(name_position, name, fill="black", font=name_font)
    
    # -------- ISSUE DATE --------
    issue_date = datetime.now()
    issue_text = issue_date.strftime("%d %B %Y")
    
    draw.text((200, height - 200),
              f"Issue Date: {issue_text}",
              fill="black",
              font=text_font)
    
    # -------- EXPIRY DATE --------
    expiry_date = issue_date + timedelta(days=365 * 2)  # 2 year validity
    expiry_text = expiry_date.strftime("%d %B %Y")
    
    draw.text((900 if width > 1000 else 500, height - 200),
              f"Expiry Date: {expiry_text}",
              fill="black",
              font=text_font)
    
    # -------- CERTIFICATE ID --------
    cert_id_text = f"Cert ID: {cert_id}"
    draw.text((width - 400, 100),
              cert_id_text,
              fill="black",
              font=text_font)
    
    # Save the certificate
    if output_path is None:
        # Save to media/certificates folder
        cert_dir = os.path.join(settings.MEDIA_ROOT, 'certificates')
        os.makedirs(cert_dir, exist_ok=True)
        output_path = os.path.join(cert_dir, f"{cert_id}.png")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    img.save(output_path, "PNG")
    
    return output_path


def generate_user_certificate(user, force=False):
    """
    Generate certificate for a user who completed all machines
    
    Args:
        user: Django User object
        force: If True, skip completion check (for admins/testing)
    
    Returns:
        Certificate object or None if not eligible
    """
    from .models import Machine, Certificate, MachineSubmission
    
    # Check if user completed all machines (skip for superusers or force=True)
    total_machines = Machine.objects.count()
    if total_machines == 0:
        return None
    
    # Skip completion check for superusers or when force=True
    if not (user.is_superuser or force):
        # Count user's completed machines (both user and root flags)
        completed_count = MachineSubmission.objects.filter(
            user=user,
            flag_type__in=['user', 'root']
        ).values('machine').distinct().count()
        
        # Check if user completed all machines
        if completed_count < total_machines:
            return None
    
    # Check if certificate already exists
    existing_cert = Certificate.objects.filter(user=user).first()
    if existing_cert:
        return existing_cert
    
    # Generate new certificate
    cert_id = generate_certificate_id()
    expiry_date = datetime.now() + timedelta(days=365 * 2)
    
    # Create certificate record
    certificate = Certificate.objects.create(
        user=user,
        certificate_id=cert_id,
        expiry_date=expiry_date
    )
    
    # Generate certificate image
    try:
        image_path = create_certificate(user.username, cert_id)
        # Save relative path
        certificate.certificate_image = f'certificates/{cert_id}.png'
        certificate.save()
    except Exception as e:
        print(f"Error generating certificate image: {e}")
    
    return certificate


def check_user_eligibility(user):
    """
    Check if user is eligible for certificate
    
    Returns:
        dict with eligibility status and progress
    """
    from .models import Machine, MachineSubmission
    
    total_machines = Machine.objects.count()
    if total_machines == 0:
        return {
            'eligible': False,
            'message': 'No machines available',
            'completed': 0,
            'total': 0
        }
    
    completed_count = MachineSubmission.objects.filter(
        user=user,
        flag_type__in=['user', 'root']
    ).values('machine').distinct().count()
    
    eligible = completed_count >= total_machines
    
    return {
        'eligible': eligible,
        'completed': completed_count,
        'total': total_machines,
        'message': f'{completed_count}/{total_machines} machines completed'
    }
