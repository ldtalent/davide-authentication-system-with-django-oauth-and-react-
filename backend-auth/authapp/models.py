import os
from PIL import ImageDraw, ImageFont
from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    mobile_number = models.CharField(max_length=20)
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics', null=True, blank=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def __str__(self):
        return self.user.username

    def generate_thumbnail(self):
        if not self.profile_picture:
            if self.user.first_name:
                initials = self.user.first_name[:2].upper()
                thumbnail_size = (100, 100)
                thumbnail_directory = os.path.join(settings.MEDIA_ROOT, 'profile_pics', 'thumbnails')
                os.makedirs(thumbnail_directory, exist_ok=True)
                thumbnail_path = os.path.join(thumbnail_directory, f"{initials}.png")

                try:
                    # Create a new blank thumbnail image
                    thumbnail_image = Image.new("RGB", thumbnail_size, (255, 255, 255))

                    # Draw initials on the thumbnail image
                    draw = ImageDraw.Draw(thumbnail_image)
                    font = ImageFont.load_default()  # Use the default font
                    text_size = font.getsize(font)
                    text_position = ((thumbnail_size[0] - text_size[0]) // 2, (thumbnail_size[1] - text_size[1]) // 2)
                    draw.text(text_position, initials, font=font, fill=(0, 0, 0))

                    # Save the generated thumbnail image
                    thumbnail_image.save(thumbnail_path)

                    self.profile_picture = thumbnail_path
                    self.save()
                    print("Thumbnail generated successfully")
                except Exception as e:
                    print(f"Error occurred during thumbnail generation: {str(e)}")
            else:
                print("No profile picture or first name provided")
        else:
            print("Profile picture already exists")
