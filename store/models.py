from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_extensions.db.fields import AutoSlugField
from django_countries.fields import CountryField
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.timezone import now
from datetime import timedelta
from django.utils import timezone
from django.db.models import IntegerField, Value, Case, When, CharField
from django.db.models.functions import Cast

ADDRESS_CHOICES = (
    ('B', 'Rechnungsadresse'),
    ('S', 'Lieferadresse'),
)

PAYMENT_CHOICES = (
	('R', 'Rechnung*'),
	('V', 'Vorkasse (2% Skonto)'),
	)

CONDITION_CHOICES = (
	('G', 'Gebraucht'),
	('N', 'Neu')
	)

ANONYM_CHOICES = (
	('Ja', 'Ja'),
	('Nein', 'Nein')
	)

KANTON_CHOICES = (
	("", "Kanton wählen"),
    ('Aargau', 'Aargau'),
    ('Appenzell Innerrhoden', 'Appenzell Innerrhoden'),
    ('Appenzell Ausserrhoden', 'Appenzell Ausserrhoden'),
    ('Bern', 'Bern'),
    ('Basel-Landschaft', 'Basel-Landschaft'),
    ('Basel-Stadt', 'Basel-Stadt'),
    ('Freiburg', 'Freiburg'),
    ('Genf', 'Genf'),
    ('Glarus', 'Glarus'),
    ('Graubünden', 'Graubünden'),
    ('Jura', 'Jura'),
    ('Luzern', 'Luzern'),
    ('Neuenburg', 'Neuenburg'),
    ('Nidwalden', 'Nidwalden'),
    ('Obwalden', 'Obwalden'),
    ('St. Gallen', 'St. Gallen'),
    ('Schaffhausen', 'Schaffhausen'),
    ('Solothurn', 'Solothurn'),
    ('Schwyz', 'Schwyz'),
    ('Thurgau', 'Thurgau'),
    ('Tessin', 'Tessin'),
    ('Uri', 'Uri'),
    ('Waadt', 'Waadt'),
    ('Wallis', 'Wallis'),
    ('Zug', 'Zug'),
    ('Zürich', 'Zürich'),
)





class LieferantenStatus(models.Model):
    date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    order = models.ForeignKey("LieferantenBestellungen", on_delete=models.CASCADE, related_name="status_updates")
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Status {self.id}: {self.name}" if self.name else f"Status {self.id}"  


class LieferantenBestellungen(models.Model):
    start_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    kunden_nr = models.CharField(max_length=255, null=True, blank=True)
    status = models.ManyToManyField(LieferantenStatus, related_name='bestellungen_status', blank=True)
    lieferant = models.ForeignKey("Lieferanten", on_delete=models.CASCADE, null=True, blank=True, related_name="lieferanten_id")
    auftrag = models.ForeignKey("Elemente_Bestellungen", on_delete=models.CASCADE, null=True, blank=True, related_name="auftrag")

    class Meta:
        ordering = ['id']
        verbose_name = 'Lieferanten-Bestellung'
        verbose_name_plural = 'Lieferanten-Bestellungen'

    def __str__(self):
        return f"Bestellung {self.id} - Kunde: {self.kunden_nr}" if self.kunden_nr else f"Bestellung {self.id}"  


class LieferantenBestellungenArtikel(models.Model):
    order = models.ForeignKey(LieferantenBestellungen, on_delete=models.CASCADE, related_name="artikel_bestellungen")
    artikel = models.ForeignKey("Artikel", on_delete=models.CASCADE, related_name="lieferanten_artikel")
    anzahl = models.PositiveIntegerField(verbose_name="Anzahl")

    def __str__(self):
        return f"Artikel {self.artikel.id} - Anzahl: {self.anzahl}"




WER_CHOICES = [
    ('lager', 'Lager'),
    ('lieferant', 'Lieferant'),
    ('produktion', 'Produktion'),
]

class Elemente_Bestellungen(models.Model):
    start_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    kunden_nr = models.CharField(max_length=255, null=True, blank=True)
    montage = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, default="offen", verbose_name="Status")
    notizfeld = models.CharField(max_length=500, null=True, blank=True, verbose_name="Notizfeld")
    wer = models.CharField(max_length=50, choices=WER_CHOICES, null=True, blank=True,default="lager", verbose_name="Zuständigkeit")
  
    class Meta:
        ordering = ['id']
        verbose_name = 'Elemente Bestellung'
        verbose_name_plural = 'Elemente Bestellungen'

    def __str__(self):
        return f"{self.kunden_nr}"


class ElementeCartItem(models.Model):
    order = models.ForeignKey(Elemente_Bestellungen, on_delete=models.CASCADE, related_name="elementeitems_bestellung")
    element_nr = models.ForeignKey("Elemente", on_delete=models.CASCADE, related_name="elemente_cart_items")  # ForeignKey to Elemente model
    artikel = models.ForeignKey("Artikel", on_delete=models.CASCADE, related_name="elementebestellung_artikel", null=True, blank=True)
    anzahl = models.PositiveIntegerField(verbose_name="Anzahl")

    def get_artikel(self):
        """ Fetch the related Artikel object through Elemente """
        element = Elemente.objects.filter(elementnr=self.element_nr_id).select_related("artikel").first()
        return element.artikel if element and element.artikel else None

    def __str__(self):
        artikel = self.get_artikel()
        artikelnr = artikel.artikelnr if artikel else "Kein Artikel"
        return f"Item {self.id} - Element-Nr.: {self.element_nr.elementnr}, Bezeichnung: {self.element_nr.bezeichnung}, Artikel-Nr.: {artikelnr}, Anzahl: {self.anzahl}"


class Subcategory(models.Model):
	sub_name = models.CharField(max_length=255)
	sub_slug = models.SlugField(max_length=255)

	class Meta:
		ordering = ['sub_name']
		verbose_name = 'Subkategorie'
		verbose_name_plural = 'Subkategorien'

	def __str__(self):
		return self.sub_name


class Category(models.Model):
	name = models.CharField(max_length=255)
	slug = models.SlugField(max_length=255)
	categorypic = models.ImageField(null=True, blank=True, upload_to="produktbilder/")

	class Meta:
		ordering = ['id']
		verbose_name = 'Kategorie'
		verbose_name_plural = 'Kategorien'

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('home')


        
class Item(models.Model):
	titel = models.CharField(max_length=255)
	preis = models.FloatField()
	preis2 = models.FloatField(null=True, blank=True,)
	preis3 = models.FloatField(null=True, blank=True,)
	preis4 = models.FloatField(null=True, blank=True,)
	preis5 = models.FloatField(null=True, blank=True,)
	preis6 = models.FloatField(null=True, blank=True,)
	preis7 = models.FloatField(null=True, blank=True,)
	kurzbeschreibung = models.CharField(max_length=500, default='')
	beschreibung = models.CharField(max_length=500, default='')
	lieferung = models.CharField(max_length=255, null=True, blank=True,default="ca. 5 bis 7 Tage")
	montage = models.CharField(max_length=255, null=True, blank=True,)
	kategorie = models.ForeignKey(Category, default=1, on_delete=models.SET_NULL, null=True, blank=True)
	subkategorie = models.ForeignKey(Subcategory, default=None, on_delete=models.SET_NULL, null=True, blank=True)
	titelbild = models.ImageField(null=True, blank=True, upload_to="produktbilder/")
	slug = models.SlugField(max_length=255)
	artikelnr = models.CharField(max_length=255)
	farbe = models.CharField(max_length=255, null=True, blank=True,)
	nut = models.CharField(max_length=255, null=True, blank=True,)
	falz = models.CharField(max_length=255, null=True, blank=True,)
	falzluft = models.CharField(max_length=255, null=True, blank=True,)
	fuge = models.CharField(max_length=255, null=True, blank=True,)
	glasdicke = models.CharField(max_length=255, null=True, blank=True,)
	material = models.CharField(max_length=255, null=True, blank=True,)
	hersteller = models.CharField(max_length=255, null=True, blank=True,)
	sortierung = models.IntegerField(null=True, blank=True)

	class Meta:
		verbose_name = 'Produkte'
		verbose_name_plural = 'Produkte'
		ordering = ['-artikelnr']

	def __str__(self):
		return str(self.kategorie) + ' ' + str(self.subkategorie) + ' ' + str(self.artikelnr)

	def get_absolute_url(self):
		return reverse('store:pdescription', kwargs={"slug": self.slug})

	def get_remove_from_cart_url(self):
		return reverse('store:remove_from_cart', kwargs={"slug": self.slug})

class Marke(models.Model):
	name = models.CharField(max_length=255)
	slug = models.SlugField(max_length=255)
	markepic = models.ImageField(null=True, blank=True, upload_to="markebilder/")
	marketext = models.TextField(blank=True)
	bestseller = models.BooleanField(default=False)
	item = models.ManyToManyField(Item, related_name='item_marken', blank=True)

	class Meta:
		ordering = ['id']
		verbose_name = 'Marke'
		verbose_name_plural = 'Marken'

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('home')
		
class OrderItem(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	ordered = models.BooleanField(default=False)
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)
	aussenbreite = models.IntegerField(null=True, blank=True, default=250)
	aussenhöhe = models.IntegerField(null=True, blank=True, default=250)
	element = models.IntegerField(null=True, blank=True)

	def __str__(self):
		return f"{str(self.pk)} / {self.quantity} Stück von Artikel-Nr. {self.item.artikelnr} {self.item.titel} / AB {self.aussenbreite} AH {self.aussenhöhe} / CHF {self.item.preis} pro Stück"

	def get_add_to_cart_url(self):
		return reverse('store:add_to_cart', kwargs={"slug": self.item.slug, "pk": self.pk})

	def get_add_to_cart_url_myd(self):
		return reverse('store:add_to_cart_myd', kwargs={"slug": self.item.slug, "pk": self.pk})

	def get_laufmeter_total(self):
		return (self.aussenbreite * 2 / 1000) + (self.aussenhöhe * 2 / 1000)

	def get_stueck_price_gummi(self):
		if self.quantity >= 25:
			if self.quantity < 50:
				return self.item.preis2
			else:
				if self.quantity >= 50:
					if self.quantity < 100:
						return self.item.preis3
					else:
						if self.quantity >=100:
							if self.quantity < 200:
								return self.item.preis4
							else:
								if self.quantity >=200:
									if self.quantity < 500:
										return self.item.preis5
									else:
										if self.quantity >=500:
											return self.item.preis6
		else:
			return self.item.preis

	def get_stueck_price(self):
		if self.quantity >= 5:
			if self.quantity < 10:
				return self.item.preis2
			else:
				if self.quantity >= 10:
					if self.quantity < 25:
						return self.item.preis3
					else:
						if self.quantity >=25:
							if self.quantity < 50:
								return self.item.preis4
							else:
								if self.quantity >=50:
									return self.item.preis5
		else:
			return self.item.preis

	def get_meter_price(self):
		if self.quantity >= 25:
			if self.quantity < 50:
				return self.item.preis2
			else:
				if self.quantity >= 50:
					if self.quantity < 100:
						return self.item.preis3
					else:
						if self.quantity >=100:
							if self.quantity < 200:
								return self.item.preis4
							else:
								if self.quantity >=200:
									if self.quantity < 500:
										return self.item.preis5
									else:
										if self.quantity >=500:
											if self.quantity < 1000:
												return self.item.preis6
											else:
												if self.quantity >=1000:
													return self.item.preis7
											
		else:
			return self.item.preis

	def get_price(self):
		if self.item.kategorie.name == 'Weitere Dichtungen':
			if self.item.subkategorie.sub_name == 'Duschdichtungen':
				return self.get_stueck_price()
			else:
				return self.get_meter_price()

		else:
			if self.item.kategorie.name == 'Gummidichtung' or self.item.kategorie.name == 'EPDM/Moosgummi':
				return self.get_stueck_price_gummi()
			else:
				if self.get_laufmeter_total() >= 2:
					if self.get_laufmeter_total() < 4:
						return self.item.preis2
					else: 
						return self.item.preis3
				else:
					return self.item.preis	

	def get_total_pre(self):
		return self.quantity  * self.get_price()
	
	def get_total_item_price(self):
		return self.quantity  * self.get_price() * ((self.aussenbreite * 2 / 1000) + (self.aussenhöhe * 2 / 1000))

	def get_final_price(self):
		return self.get_total_item_price()

	def get_total_item_price_pvc(self):
		return self.get_total_item_price() / self.quantity

	def get_total_item_price_pvc_total(self):
		return self.get_total_item_price_pvc() * self.quantity 


class ShippingCost(models.Model):
	price_from = models.FloatField(null=True, blank=True,)
	price_to = models.FloatField(null=True, blank=True,)
	shipping_price = models.FloatField(null=True, blank=True,)

	def __str__(self):
		return 'Von CHF ' + str(self.price_from) + ' bis CHF ' + str(self.price_to) + ' Versand: CHF ' + str(self.shipping_price)

class Order(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	items = models.ManyToManyField('OrderItem')
	start_date = models.DateTimeField(auto_now_add=True)
	ordered_date = models.DateTimeField()
	ordered = models.BooleanField(default=False)
	billing_address = models.ForeignKey(
		'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
	shipping_address = models.ForeignKey(
		'ShippingAddress', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
	payment = models.BooleanField(default=False)
	payment_method = models.CharField(max_length=255, choices=PAYMENT_CHOICES, default="R")
	shippingcost = models.FloatField(null=True, blank=True, default=0)
	discount = models.FloatField(null=True, blank=True)
	discount_pct = models.FloatField(null=True, blank=True)
	skonto = models.FloatField(null=True, blank=True)
	pre_total = models.FloatField(null=True, blank=True)
	order_mwst = models.FloatField(null=True, blank=True)
	total = models.FloatField(null=True, blank=True)

	class Meta:
		verbose_name = 'Bestellung'
		verbose_name_plural = 'Bestellungen'
		ordering = ['-ordered_date']

	def __str__(self):
		return self.user.username + ' ' + str(self.start_date) + ' ' + str(self.ordered)

	def get_payment_method(self):
		return [i[1] for i in Order._meta.get_field('payment_method').choices if i[0] == self.payment_method][0]

	@property
	def get_total(self):
		total = 0
		for order_item in self.items.all():
			total += order_item.get_final_price()
		return total

	@property
	def get_shipping(self):
		return self.shippingcost or 0

	@property
	def get_total_product_and_shipping(self):
		return self.get_total + self.get_shipping

	@property
	def get_rabatt(self):
		rabatt_prozent = self.user.profile.rabatt
		return self.get_total * (rabatt_prozent / 100)

	@property
	def rabatt(self):
		return self.user.profile.rabatt / 100

	@property
	def get_total_pre_mwst_withoutskonto(self):
		return self.get_total_product_and_shipping - self.get_rabatt

	@property
	def get_skonto(self):
		if self.payment_method == 'V':
			return 0.02 * self.get_total_pre_mwst_withoutskonto
		return 0

	@property
	def get_total_pre_mwst(self):
		return self.get_total_product_and_shipping - self.get_rabatt - self.get_skonto

	@property
	def grandtotal(self):
		return self.get_total_pre_mwst * 1.081

	@property
	def mwst(self):
		return self.grandtotal - self.get_total_pre_mwst

	@property
	def get_total_mwst_warenkorb(self):
		return self.get_total_pre_mwst_withoutskonto * 1.081

	@property
	def get_pre_mwst_warenkorb(self):
		return self.get_total_mwst_warenkorb - self.get_total_pre_mwst_withoutskonto


class Address(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name ='address', on_delete=models.CASCADE)
	rechnung_strasse = models.CharField(max_length=255)
	rechnung_nr = models.CharField(max_length=255)
	rechnung_ort = models.CharField(max_length=255)
	rechnung_land = CountryField(multiple=False)
	rechnung_plz = models.CharField(max_length=255)
	address_type = models.CharField(max_length=500, choices=ADDRESS_CHOICES)

	class Meta:
		verbose_name = 'Rechnungsadresse'
		verbose_name_plural = 'Rechnungsadressen'

	def __str__(self):
		return self.user.username + ' ' + str(self.rechnung_strasse) + ' '+ str(self.rechnung_nr) + ', ' + str(self.rechnung_plz) + ' '+ str(self.rechnung_ort)

class ShippingAddress(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name ='shipping_address', on_delete=models.CASCADE,null=True, blank=True)
	lieferung_strasse = models.CharField(max_length=255)
	lieferung_nr = models.CharField(max_length=255)
	lieferung_ort = models.CharField(max_length=255)
	lieferung_land = CountryField(multiple=False)
	lieferung_plz = models.CharField(max_length=255)
	address_type = models.CharField(max_length=500, choices=ADDRESS_CHOICES)
	vorname = models.CharField(max_length=255, null=True, blank=True)
	nachname = models.CharField(max_length=255, null=True, blank=True)
	firmenname = models.CharField(max_length=255, null=True, blank=True)

	class Meta:
		verbose_name = 'Lieferadresse'
		verbose_name_plural = 'Lieferadressen'

	def __str__(self):
		return self.user.username + ' ' + str(self.lieferung_strasse) + ' '+ str(self.lieferung_nr) + ', ' + str(self.lieferung_plz) + ' '+ str(self.lieferung_ort)

# new model -> Bezeichnung creating and connect to Elemente model
class Bezeichnung(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Kunde(models.Model):
	user = models.OneToOneField(User, unique=True, related_name ='profile', on_delete=models.CASCADE,null=True, blank=True)
	firmenname = models.CharField(max_length=255, null=True, blank=True)
	rabatt = models.FloatField(null=True, blank=True)
	newsletter = models.BooleanField(null=True, blank=True)
	mobile = models.CharField(max_length=255, null=True, blank=True) 
	phone = models.CharField(max_length=255, null=True, blank=True) 
	birthday = models.CharField(max_length=255, null=True, blank=True)
	interne_nummer = models.IntegerField(null=True, blank=True)
	email = models.CharField(max_length=255, null=True, blank=True)
	vorname = models.CharField(max_length=255, null=True, blank=True)
	nachname = models.CharField(max_length=255, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
	last_service = models.DateTimeField(null=True, blank=True)
	zusatz = models.CharField(max_length=255, null=True, blank=True)
	done = models.BooleanField(default=False)

	class Meta:
		ordering = ['id']
		verbose_name = 'Kunde'
		verbose_name_plural = 'Kunden'

	def __str__(self):
        # Convert any datetime or timedelta object to a string
		return f"{self.firmenname or 'Kunde'}"

	# Method to calculate the due date (1 year after the last service)
	def get_due_date(self):
		if self.last_service:
			return self.last_service + timedelta(days=365)  # Add 1 year
		return None


	def get_absolute_crm_url(self):
		return reverse('store:crm_new_kunde_bearbeiten', kwargs={'pk': self.pk})

	def get_absolute_url(self):
		return reverse('store:cms_kunde_bearbeiten', kwargs={'pk': self.pk})

	def get_absolute_address_url(self):
		return reverse('store:cms_kundenadresse_bearbeiten', kwargs={'pk': self.pk})

	def get_absolute_crm_address_url(self):
		return reverse('store:cms_crm_adresse_bearbeiten', kwargs={'pk': self.pk})

	def get_absolute_elemente_url(self):
		return reverse('store:cms_elemente', kwargs={'pk': self.pk})

	def elemente_count(self):
		return self.kunden_elemente.count()


class CRMLager(models.Model):
	titel = models.CharField(max_length=255, null=True, blank=True)
	aussenbreite = models.IntegerField(null=True, blank=True)
	aussenhöhe = models.IntegerField(null=True, blank=True)
	dichtungstyp = models.CharField(max_length=255, null=True, blank=True)
	lagerort = models.CharField(max_length=255, null=True, blank=True)
	lagerbestand = models.IntegerField(null=True, blank=True, default=1)
	marke = models.ForeignKey('Marke', on_delete=models.SET_NULL, null=True, blank=True, related_name='lager_marke')

	class Meta:
		verbose_name = 'CRM-Lager'
		verbose_name_plural = 'CRM-Lagerbestände'

	def __str__(self):
		return self.titel


class CRMAddress(models.Model):
	kunde = models.ForeignKey(Kunde, related_name ='kunde_address', on_delete=models.CASCADE)
	crm_strasse = models.CharField(max_length=255, null=True, blank=True)
	crm_nr = models.CharField(max_length=255, null=True, blank=True)
	crm_ort = models.CharField(max_length=255, null=True, blank=True)
	crm_land = CountryField(multiple=False)
	crm_plz = models.CharField(max_length=255, null=True, blank=True)
	crm_kanton = models.CharField(max_length=255, null=True, blank=True, choices=KANTON_CHOICES, default="")
	address_type = models.CharField(max_length=500, null=True, blank=True, choices=ADDRESS_CHOICES)

	class Meta:
		verbose_name = 'CRM-Adresse'
		verbose_name_plural = 'CRM-Adressen'

	def __str__(self):
		return self.user.firmenname + ' ' + str(self.crm_strasse)


class Lieferanten(models.Model):
	number = models.IntegerField(null=True, blank=True)
	our_kundennumber = models.IntegerField(null=True, blank=True)
	name = models.CharField(max_length=255, null=True, blank=True) 
	adresse = models.CharField(max_length=255, null=True, blank=True) 
	plz = models.CharField(max_length=255, null=True, blank=True) 
	ort = models.CharField(max_length=255, null=True, blank=True)
	email = models.CharField(max_length=255, null=True, blank=True)

	class Meta:
		ordering = ['id']
		verbose_name = 'Lieferant'
		verbose_name_plural = 'Lieferanten'

	def __str__(self):
		return self.name or "Unbekannter Lieferant"


class Preiscode(models.Model):
	preiscode = models.CharField(max_length=255, unique=True, null=False, blank=False) 
	faktor = models.FloatField(null=True, blank=True)
	transportkosten = models.IntegerField(null=True, blank=True)
	rabatt = models.IntegerField(null=True, blank=True)
	preisanpassung = models.IntegerField(null=True, blank=True)
	
	class Meta:
		ordering = ['preiscode']
		verbose_name = 'Preiscode'
		verbose_name_plural = 'Preiscodes'

	def __str__(self):
		return f"{self.preiscode or 'Keine Nummer'} - {self.faktor or 'Unbenannt'}"

class ArtikelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            artikelnr_numeric=Case(
                When(artikelnr__regex=r'^\d+$', then=Cast('artikelnr', IntegerField())),  # Cast numeric strings
                default=Value(0),  # Fallback for non-numeric values
                output_field=IntegerField()
            )
        ).order_by('artikelnr_numeric', 'artikelnr')

class Artikel(models.Model):
    artikelnr = models.CharField(max_length=255, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    lieferant = models.ForeignKey(Lieferanten, related_name='artikel_lieferanten', on_delete=models.SET_NULL, null=True, blank=True)
    lieferantenartikel = models.CharField(max_length=255, unique=True, null=True, blank=True) 
    aussenbreite = models.IntegerField(null=True, blank=True)
    aussenhöhe = models.IntegerField(null=True, blank=True)
    nettopreis = models.FloatField(null=True, blank=True)
    zubehoerartikelnr = models.CharField(max_length=255, null=True, blank=True)
    lagerbestand = models.IntegerField(null=True, blank=True, default=0)
    lagerort = models.CharField(max_length=255, null=True, blank=True)
    preiscode = models.ForeignKey(Preiscode, related_name='artikel_preiscode', on_delete=models.SET_NULL, null=True, blank=True)
    bestpreis = models.FloatField(null=True, blank=True)
    bestpreis_lieferant = models.ForeignKey(Lieferanten, related_name='artikel_lieferanten_bestpreis', on_delete=models.SET_NULL, null=True, blank=True)
    lieferanten_artikelnummern = models.CharField(max_length=255, null=True, blank=True)
    dichtungstypen = models.CharField(max_length=255, null=True, blank=True)


    # Attach custom manager
    objects = ArtikelManager()

    class Meta:
        verbose_name = 'Artikel'
        verbose_name_plural = 'Artikel'

    def __str__(self):
        return f"{self.artikelnr or 'Keine Nummer'} - {self.name or 'Unbenannt'}"

    @property
    def vp(self):
        """
        Verkaufspreis (vp) is calculated as nettopreis * preiscode.faktor.
        """
        if self.nettopreis is not None and self.preiscode and self.preiscode.faktor is not None:
            return round(self.nettopreis * self.preiscode.faktor, 2)
        return None

class Elemente(models.Model):
	dichtungen = models.ForeignKey(
		'Item', on_delete=models.SET_NULL, blank=True, null=True)
	produkt = models.CharField(max_length=255, blank=True, null=True)
	elementnr = models.IntegerField(null=True, blank=True) 
	kuehlposition = models.CharField(max_length=255)
	bemerkung = models.CharField(max_length=255, blank=True, null=True)
	kunde = models.ManyToManyField(Kunde, related_name='kunden_elemente', blank=True)
	aussenbreite = models.IntegerField(null=True, blank=True)
	aussenhöhe = models.IntegerField(null=True, blank=True)
	produkt = models.CharField(max_length=255, blank=True, null=True)
	number = models.CharField(max_length=255, blank=True, null=True)
	nettopreis = models.CharField(max_length=255, blank=True, null=True)
	lieferant = models.ForeignKey(Lieferanten, related_name ='elemente_lieferanten', on_delete=models.SET_NULL, null=True, blank=True)
	artikel = models.ForeignKey(Artikel, related_name='artikel_elemente', on_delete=models.SET_NULL, null=True, blank=True)
	bezeichnung = models.CharField(max_length=255, blank=True, null=True)
	bezeichnung_new = models.ForeignKey(Bezeichnung, related_name='elementebezeichnung', on_delete=models.SET_NULL, null=True, blank=True)

	def elemente_laufmeter(self):
	    # Use the dimensions from `Elemente` if available
	    breite = self.aussenbreite
	    hoehe = self.aussenhöhe

	    # Fallback to dimensions from the related `Artikel` if available
	    if (breite is None or hoehe is None) and self.artikel:
	        artikel_breite = getattr(self.artikel, 'aussenbreite', None)
	        artikel_hoehe = getattr(self.artikel, 'aussenhöhe', None)
	        breite = breite if breite is not None else artikel_breite
	        hoehe = hoehe if hoehe is not None else artikel_hoehe

	    # Ensure dimensions are valid before calculating laufmeter
	    if breite is not None and hoehe is not None:
	        lfm = (2 * (breite + hoehe)) / 1000
	        return lfm

	    # Return 0 if dimensions are still not available
	    return 0


	class Meta:
		ordering = ['elementnr']
		verbose_name = 'Element'
		verbose_name_plural = 'Elemente'

	def __str__(self):
		return f"{self.elementnr}" 


class Objekte(models.Model):
	name = models.CharField(max_length=255, null=True, blank=True) 
	objekte = models.ManyToManyField(Elemente, related_name='elemente_objekte', blank=True)
	serie = models.CharField(max_length=255, null=True, blank=True) 
	modell = models.CharField(max_length=255, null=True, blank=True)
	typ = models.CharField(max_length=255, null=True, blank=True)
	lieferant = models.ForeignKey(Lieferanten, related_name ='objekte_lieferanten', on_delete=models.CASCADE, null=True, blank=True)

	class Meta:
		ordering = ['id']
		verbose_name = 'Objekt'
		verbose_name_plural = 'Objekte'

	def __str__(self):
		return str(self.serie) + ' ' + self.modell + ' ' + self.typ