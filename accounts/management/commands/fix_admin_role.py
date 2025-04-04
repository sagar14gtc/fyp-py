from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings

CustomUser = get_user_model()

class Command(BaseCommand):
    help = 'Corrects the role of the primary admin user if it is set incorrectly.'

    # Define the email of the admin user to target
    ADMIN_EMAIL = 'admin@gmail.com' # Adjust if the admin email is different

    def handle(self, *args, **options):
        try:
            admin_user = CustomUser.objects.get(email=self.ADMIN_EMAIL)

            if not admin_user.is_superuser:
                self.stdout.write(self.style.WARNING(f"User {self.ADMIN_EMAIL} is not a superuser. No role change applied based on superuser status."))
                # Optionally, still force the role if needed, even if not superuser
                # if admin_user.role != CustomUser.ADMIN:
                #    admin_user.role = CustomUser.ADMIN
                #    admin_user.save()
                #    self.stdout.write(self.style.SUCCESS(f"Role for {self.ADMIN_EMAIL} set to ADMIN."))
                # else:
                #    self.stdout.write(f"User {self.ADMIN_EMAIL} already has the ADMIN role.")

            elif admin_user.role != CustomUser.ADMIN:
                original_role = admin_user.role
                admin_user.role = CustomUser.ADMIN
                admin_user.save()
                self.stdout.write(self.style.SUCCESS(
                    f"Role for superuser {self.ADMIN_EMAIL} corrected from '{original_role}' to '{CustomUser.ADMIN}'."
                ))
            else:
                self.stdout.write(self.style.SUCCESS(
                    f"Superuser {self.ADMIN_EMAIL} already has the correct role ('{CustomUser.ADMIN}')."
                ))

        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Admin user with email {self.ADMIN_EMAIL} not found."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))
