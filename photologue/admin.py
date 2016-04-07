from django import forms
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.sites.models import Site
from django.contrib import messages
from django.utils.translation import ungettext, ugettext_lazy as _
from django.shortcuts import render
from django.contrib.admin import helpers
from django.http import HttpResponseRedirect

from .models import Gallery, Photo, PhotoEffect, PhotoSize, \
    Watermark
from .forms import UploadZipForm

MULTISITE = getattr(settings, 'PHOTOLOGUE_MULTISITE', False)


class GalleryAdminForm(forms.ModelForm):

    class Meta:
        model = Gallery
        if MULTISITE:
            exclude = []
        else:
            exclude = ['sites']


class GalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_added', 'photo_count', 'is_public')
    list_filter = ['date_added', 'is_public']
    if MULTISITE:
        list_filter.append('sites')
    date_hierarchy = 'date_added'
    prepopulated_fields = {'slug': ('title',)}
    #prepopulated_fields = {'slug': ('title',)}
    form = GalleryAdminForm
    if MULTISITE:
        filter_horizontal = ['sites']
    if MULTISITE:
        actions = [
            'add_to_current_site',
            'add_photos_to_current_site',
            'remove_from_current_site',
            'remove_photos_from_current_site'
        ]

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """ Set the current site as initial value. """
        if db_field.name == "sites":
            kwargs["initial"] = [Site.objects.get_current()]
        return super(GalleryAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def save_related(self, request, form, *args, **kwargs):
        """
        If the user has saved a gallery with a photo that belongs only to
        different Sites - it might cause much confusion. So let them know.
        """
        super(GalleryAdmin, self).save_related(request, form, *args, **kwargs)
        orphaned_photos = form.instance.orphaned_photos()
        if orphaned_photos:
            msg = ungettext(
                'The following photo does not belong to the same site(s)'
                ' as the gallery, so will never be displayed: %(photo_list)s.',
                'The following photos do not belong to the same site(s)'
                ' as the gallery, so will never be displayed: %(photo_list)s.',
                len(orphaned_photos)
            ) % {'photo_list': ", ".join([photo.title for photo in orphaned_photos])}
            messages.warning(request, msg)

    def add_to_current_site(modeladmin, request, queryset):
        current_site = Site.objects.get_current()
        current_site.gallery_set.add(*queryset)
        msg = ungettext(
            "The gallery has been successfully added to %(site)s",
            "The galleries have been successfully added to %(site)s",
            len(queryset)
        ) % {'site': current_site.name}
        messages.success(request, msg)

    add_to_current_site.short_description = \
        _("Add selected galleries to the current site")

    def remove_from_current_site(modeladmin, request, queryset):
        current_site = Site.objects.get_current()
        current_site.gallery_set.remove(*queryset)
        msg = ungettext(
            "The gallery has been successfully removed from %(site)s",
            "The selected galleries have been successfully removed from %(site)s",
            len(queryset)
        ) % {'site': current_site.name}
        messages.success(request, msg)

    remove_from_current_site.short_description = \
        _("Remove selected galleries from the current site")

    def add_photos_to_current_site(modeladmin, request, queryset):
        photos = Photo.objects.filter(galleries__in=queryset)
        current_site = Site.objects.get_current()
        current_site.photo_set.add(*photos)
        msg = ungettext(
            'All photos in gallery %(galleries)s have been successfully added to %(site)s',
            'All photos in galleries %(galleries)s have been successfully added to %(site)s',
            len(queryset)
        ) % {
            'site': current_site.name,
            'galleries': ", ".join(["'{0}'".format(gallery.title)
                                    for gallery in queryset])
        }
        messages.success(request, msg)

    add_photos_to_current_site.short_description = \
        _("Add all photos of selected galleries to the current site")

    def remove_photos_from_current_site(modeladmin, request, queryset):
        photos = Photo.objects.filter(galleries__in=queryset)
        current_site = Site.objects.get_current()
        current_site.photo_set.remove(*photos)
        msg = ungettext(
            'All photos in gallery %(galleries)s have been successfully removed from %(site)s',
            'All photos in galleries %(galleries)s have been successfully removed from %(site)s',
            len(queryset)
        ) % {
            'site': current_site.name,
            'galleries': ", ".join(["'{0}'".format(gallery.title)
                                    for gallery in queryset])
        }
        messages.success(request, msg)

    remove_photos_from_current_site.short_description = \
        _("Remove all photos in selected galleries from the current site")

admin.site.register(Gallery, GalleryAdmin)


class PhotoAdminForm(forms.ModelForm):

    class Meta:
        model = Photo

        if MULTISITE:
            exclude = []
        else:
            fields= ('species', 'authority', 'is_validated', 'source', 'image', 'title', 'slug')
            #fields= ('species', 'authority', 'is_validated', 'source', 'image', 'title', 'slug', 'admin_orig_image_tag','admin_thumbnail',)
            #readonly_fields=('admin_orig_image_tag,)
            exclude = ['sites', 'caption', 'date_added', 'is_public', 
                       'crop_from', 'effect','caption']


class PhotoAdmin(admin.ModelAdmin):
  
    #these are settings for the main list display
    list_display = ('title', 'species', 'admin_thumbnail', 'authority', 'source', 'date_added',
                    'is_validated', 'admin_orig_image_tag' )
    list_filter = [ 'is_validated', 'species','date_added']  
    
    
    #prepopulated_fields = {'slug': ('title',)}

    readonly_fields = ('date_taken',)  
    
    fields=['image', 'title','species', 'source', 'authority', 'is_validated']
    #exclude=['slug']

    
    
    if MULTISITE:
        list_filter.append('sites')
    search_fields = ['title', 'slug', 'caption']
    list_per_page = 10
    
    if MULTISITE:
        filter_horizontal = ['sites']
    if MULTISITE:
        actions = ['add_photos_to_current_site', 'remove_photos_from_current_site']    

    #form = PhotoAdminForm
    ##TODO:  find way to unbork this hard-coded path
    change_form_template=['/home/pat/workspace/photologue/photologue/templates/admin/photologue/photo/change_form.html',]
                          
    def change_view(self, request, object_id, form_url='', extra_context=None):
        to_return=self.changeform_view(request, object_id, form_url, extra_context)
        return self.changeform_view(request, object_id, form_url, extra_context)                          
                         
    def get_fields(self, request, obj=None):
        if self.fields:
            return self.fields
        form = self.get_form(request, obj, fields=None)
        to_return=list(form.base_fields) + list(self.get_readonly_fields(request, obj))
        return list(form.base_fields) + list(self.get_readonly_fields(request, obj))

    def get_fieldsets(self, request, obj=None):
        """
        Hook for specifying fieldsets.
        """
        #to_display=['image', 'title','species', 'source', 'authority', 'is_validated']
        #self.fields = to_display
        if self.fieldsets:
            return self.fieldsets
        to_return=[(None, {'fields': self.get_fields(request, obj)})]
        #to_return=[(None, {'fields':to_display})]        
        return to_return
        
        #return [(None, {'fields': self.get_fields(request, obj)})]
    
    def get_inline_formsets(self, request, formsets, inline_instances,
                            obj=None):
        inline_admin_formsets = []
        for inline, formset in zip(inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            readonly = list(inline.get_readonly_fields(request, obj))
            prepopulated = dict(inline.get_prepopulated_fields(request, obj))
            inline_admin_formset = helpers.InlineAdminFormSet(inline, formset,
                                                              fieldsets, prepopulated, readonly, model_admin=self)
            inline_admin_formsets.append(inline_admin_formset)
        return inline_admin_formsets    

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """ Set the current site as initial value. """
        if db_field.name == "sites":
            kwargs["initial"] = [Site.objects.get_current()]
        return super(PhotoAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def add_photos_to_current_site(modeladmin, request, queryset):
        current_site = Site.objects.get_current()
        current_site.photo_set.add(*queryset)
        msg = ungettext(
            'The photo has been successfully added to %(site)s',
            'The selected photos have been successfully added to %(site)s',
            len(queryset)
        ) % {'site': current_site.name}
        messages.success(request, msg)

    add_photos_to_current_site.short_description = \
        _("Add selected photos to the current site")

    def remove_photos_from_current_site(modeladmin, request, queryset):
        current_site = Site.objects.get_current()
        current_site.photo_set.remove(*queryset)
        msg = ungettext(
            'The photo has been successfully removed from %(site)s',
            'The selected photos have been successfully removed from %(site)s',
            len(queryset)
        ) % {'site': current_site.name}
        messages.success(request, msg)

    remove_photos_from_current_site.short_description = \
        _("Remove selected photos from the current site")

    def get_urls(self):
        urls = super(PhotoAdmin, self).get_urls()
        custom_urls = [
            url(r'^upload_zip/$',
                self.admin_site.admin_view(self.upload_zip),
                name='photologue_upload_zip')
        ]
        return custom_urls + urls
    
    def upload_zip(self, request):

        context = {
            'title': _('Upload a zip archive of photos'),
            'app_label': self.model._meta.app_label,
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request)
        }

        # Handle form request
        if request.method == 'POST':
            form = UploadZipForm(request.POST, request.FILES)
            if form.is_valid():
                form.save(request=request)
                return HttpResponseRedirect('..')
        else:
            form = UploadZipForm()
        context['form'] = form
        context['adminform'] = helpers.AdminForm(form,
                                                 list([(None, {'fields': form.base_fields})]),
                                                 {})
        return render(request, 'admin/photologue/photo/upload_zip.html', context)    

    def deprecated_upload_zip(self, request):

        context = {
            'title': _('Upload a zip archive of photos'),
            'app_label': self.model._meta.app_label,
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request)
        }

        # Handle form request
        if request.method == 'POST':
            form = UploadZipForm(request.POST, request.FILES)
            if form.is_valid():
                form.save(request=request)
                return HttpResponseRedirect('..')
        else:
            form = UploadZipForm()
        context['form'] = form
        context['adminform'] = helpers.AdminForm(form,
                                                 list([(None, {'fields': form.base_fields})]),
                                                 {})
        return render(request, 'admin/photologue/photo/upload_zip.html', context)


admin.site.register(Photo, PhotoAdmin)


class PhotoEffectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'color', 'brightness',
                    'contrast', 'sharpness', 'filters', 'admin_sample')
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Adjustments', {
            'fields': ('color', 'brightness', 'contrast', 'sharpness')
        }),
        ('Filters', {
            'fields': ('filters',)
        }),
        ('Reflection', {
            'fields': ('reflection_size', 'reflection_strength', 'background_color')
        }),
        ('Transpose', {
            'fields': ('transpose_method',)
        }),
    )

admin.site.register(PhotoEffect, PhotoEffectAdmin)


class PhotoSizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'width', 'height', 'crop', 'pre_cache', 'effect', 'increment_count')
    fieldsets = (
        (None, {
            'fields': ('name', 'width', 'height', 'quality')
        }),
        ('Options', {
            'fields': ('upscale', 'crop', 'pre_cache', 'increment_count')
        }),
        ('Enhancements', {
            'fields': ('effect', 'watermark',)
        }),
    )

admin.site.register(PhotoSize, PhotoSizeAdmin)


class WatermarkAdmin(admin.ModelAdmin):
    list_display = ('name', 'opacity', 'style')


admin.site.register(Watermark, WatermarkAdmin)
