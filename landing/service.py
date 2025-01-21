import uuid
from io import BytesIO
from typing import List, Optional

from django.core.files.uploadedfile import TemporaryUploadedFile
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from PIL import Image

from .inputs import ProfileCategoryInput, ProfileInput, ProfileLinkInput
from .models.profiles import Profile, ProfileCategory, ProfileLink


class ProfileService(object):
    def create_profile(
        self, request_user_id: int, profile_input: ProfileInput
    ) -> Profile:
        try:
            profile = Profile.objects.create(
                **profile_input.model_dump(exclude_unset=True),
                user_id=request_user_id,
            )
            return profile
        except Exception as e:
            raise Exception(f'Create Profile Failed: {str(e)}')

    def update_profile(
        self, request_user_id: int, profile_id: int, profile_input: ProfileInput
    ) -> Profile:
        try:
            profile = Profile.objects.get(id=profile_id, user_id=request_user_id)
            submitted_fields = {
                key: value
                for key, value in profile_input.model_dump().items()
                if value not in [None, '']
            }

            for field, value in submitted_fields.items():
                setattr(profile, field, value)

            profile.save()
            return profile

        except Profile.DoesNotExist:
            raise Exception('Profile not found')
        except Exception as e:
            raise Exception(f'Update Profile Failed: {str(e)}')

    def _process_image(
        self, image_file: TemporaryUploadedFile
    ) -> TemporaryUploadedFile:
        image = Image.open(image_file)
        extension = image_file.name.rsplit('.', 1)[1]
        image_file_io = BytesIO()
        image.save(image_file_io, image.format)

        new_image = TemporaryUploadedFile(
            f'{uuid.uuid4()}.{extension}',
            image_file.content_type,
            image_file.size,
            image_file.charset,
        )
        new_image.write(image_file_io.getvalue())
        return new_image

    def update_profile_image(
        self, profile_id: int, image: TemporaryUploadedFile
    ) -> bool:
        try:
            profile = Profile.objects.get(id=profile_id)
            processed_image = self._process_image(image)
            profile.profile_image = processed_image
            profile.save()
            return True

        except Profile.DoesNotExist:
            raise Exception('Profile not found')
        except IOError:
            raise Exception('Error processing image')
        except Exception as e:
            raise Exception(f'Unexpected error: {str(e)}')

    def create_profile_link(
        self, profile_id: int, profile_link_input: ProfileLinkInput
    ):
        print('run create')
        try:
            profile_link = ProfileLink(
                **profile_link_input.model_dump(exclude_unset=True),
                profile_id=profile_id,
            )
            print(f'Before save - order: {profile_link.order}')
            from django.db import models

            print(
                f'Current max order:',
                ProfileLink.objects.filter(
                    profile_id=profile_id, profile_category__isnull=True
                ).aggregate(max_order=models.Max('order')),
            )
            profile_link.save()
            print(f'profile_link: {profile_link}')
            return profile_link
        except Exception as e:
            print(f'Create Link Failed: {str(e)}')
            raise Exception(f'Create Link Failed: {str(e)}')

    def update_profile_link(self, link_id: int, profile_link_input: ProfileLinkInput):
        try:
            profile_link = ProfileLink.objects.get(id=link_id)

            for field, value in profile_link_input.model_dump().items():
                if value is not None:
                    setattr(profile_link, field, value)

            profile_link.save()
            return profile_link

        except ProfileLink.DoesNotExist:
            raise Exception('Link not found')
        except Exception as e:
            raise Exception(f'Update Link Failed: {str(e)}')

    def archive_link(self, link_id: int) -> ProfileLink:
        try:
            link = ProfileLink.objects.get(id=link_id)
            link.is_deleted = True
            link.save()
            return link

        except ProfileLink.DoesNotExist:
            raise Exception('Link not found')
        except Exception as e:
            raise Exception(f'Update Link Failed: {str(e)}')

    def restore_link(self, link_id: int) -> ProfileLink:
        try:
            link = ProfileLink.objects.get(id=link_id)
            link.is_deleted = False
            link.save()
            return link

        except ProfileLink.DoesNotExist:
            raise Exception('Link not found')
        except Exception as e:
            raise Exception(f'Update Link Failed: {str(e)}')

    def delete_link(self, link_id: int) -> None:
        try:
            link = ProfileLink.objects.filter(id=link_id)
            link.delete()
        except ProfileLink.DoesNotExist:
            raise Exception('Link not found')
        except Exception as e:
            raise Exception(f'Update Link Failed: {str(e)}')

    def toggle_link_visibility(self, link_id: int, is_hidden: bool) -> ProfileLink:
        try:
            link = ProfileLink.objects.get(id=link_id)
            link.is_hidden = is_hidden
            link.save()
            return link

        except ProfileLink.DoesNotExist:
            raise Exception('Link not found')
        except Exception as e:
            raise Exception(f'Update Link Failed: {str(e)}')

    def create_profile_category(self, profile_id: int) -> ProfileCategory:
        try:
            category = ProfileCategory.objects.create(
                profile_id=profile_id, title='', is_hidden=True
            )
            return category

        except Exception as e:
            raise Exception(f'Update Link Failed: {str(e)}')

    def update_profile_category(
        self, category_id: int, profile_category_input: ProfileCategoryInput
    ):
        try:
            category = ProfileCategory.objects.get(id=category_id)

            for field, value in profile_category_input.model_dump().items():
                if value is not None:
                    setattr(category, field, value)

            category.save()
            return category

        except ProfileCategory.DoesNotExist:
            raise Exception('Collection not found')
        except Exception as e:
            raise Exception(f'Update Collection Failed: {str(e)}')

    def toggle_category_visibility(
        self, category_id: int, is_hidden: bool
    ) -> ProfileLink:
        try:
            category = ProfileCategory.objects.get(id=category_id)
            category.is_hidden = is_hidden
            category.save()
            return category

        except ProfileCategory.DoesNotExist:
            raise Exception('Category not found')
        except Exception as e:
            raise Exception(f'Update Category Failed: {str(e)}')

    def delete_category(self, category_id: int) -> None:
        try:
            with transaction.atomic():
                ProfileLink.objects.filter(profile_category_id=category_id).update(
                    profile_category=None, is_deleted=True
                )

                category = ProfileCategory.objects.filter(id=category_id)
                category.delete()

        except ProfileCategory.DoesNotExist:
            raise Exception('Category not found')
        except Exception as e:
            raise Exception(f'Failed to delete category: {str(e)}')

    def update_links_order(self, link_ids: List[int]):
        try:
            link_ids = list(reversed(link_ids))
            link_map = {l.id: l for l in ProfileLink.objects.filter(id__in=link_ids)}

            with transaction.atomic():
                temp_order = 99999
                to_update = list()

                for link_id in link_ids:
                    link = link_map.get(link_id)
                    link.order = temp_order
                    to_update.append(link)
                    temp_order += 1

                ProfileLink.objects.bulk_update(
                    to_update, fields=['order', 'updated_at']
                )

                to_update = list()
                for index, link_id in enumerate(link_ids):
                    link = link_map.get(link_id)
                    link.order = index
                    to_update.append(link)

                ProfileLink.objects.bulk_update(
                    to_update, fields=['order', 'updated_at']
                )

        except Exception as e:
            print(f'exception: {e}')
            raise Exception(f'Update link order failed: {str(e)}')

    def update_categories_order(self, category_ids: List[int]):
        try:
            category_ids = list(reversed(category_ids))
            category_map = {
                c.id: c for c in ProfileCategory.objects.filter(id__in=category_ids)
            }
            with transaction.atomic():
                temp_order = 99999
                to_update = list()

                for category_id in category_ids:
                    category = category_map.get(category_id)
                    category.order = temp_order
                    to_update.append(category)
                    temp_order += 1

                ProfileCategory.objects.bulk_update(
                    to_update, fields=['order', 'updated_at']
                )

                to_update = list()
                for index, category_id in enumerate(category_ids):
                    category = category_map.get(category_id)
                    category.order = index
                    to_update.append(category)

                ProfileCategory.objects.bulk_update(
                    to_update, fields=['order', 'updated_at']
                )
        except Exception as e:
            print(f'exception: {e}')
            raise Exception(f'Update category order failed: {str(e)}')

    def update_link_category(
        self, link_id: int, category_id: Optional[int], profile: Profile
    ) -> None:
        try:
            with transaction.atomic():
                link = ProfileLink.objects.get(id=link_id, profile=profile)

                if category_id is not None:
                    category = ProfileCategory.objects.get(
                        id=category_id, profile=profile
                    )
                    link.profile_category = category
                else:
                    link.profile_category = None

                link.save(update_fields=['profile_category', 'updated_at'])

        except ProfileLink.DoesNotExist:
            raise Exception('Link not found or permission denied')
        except ProfileCategory.DoesNotExist:
            raise Exception('Category not found or permission denied')
        except Exception as e:
            raise Exception(f'Failed to update link category: {str(e)}')

    def update_link_click_count(self, link_id: int) -> None:
        try:
            ProfileLink.objects.filter(id=link_id).update(
                click_count=F('click_count') + 1, updated_at=timezone.now()
            )
        except Exception as e:
            raise Exception(f'Failed to update link click count: {str(e)}')
