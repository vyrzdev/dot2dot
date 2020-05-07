import mongoengine
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


# To be honest, kind of unnecessary.
# Only an admin user exists.
class user(mongoengine.Document):
    name = mongoengine.StringField()
    email = mongoengine.EmailField()
    address = mongoengine.DictField()
    passwordHash = mongoengine.StringField()
    metaData = mongoengine.DictField()

    def setPassword(self, password):
        self.passwordHash = generate_password_hash(password)

    def checkPassword(self, password):
        return check_password_hash(self.passwordHash, password)


class manufacturer(mongoengine.Document):
    iterID = mongoengine.SequenceField(primary_key=True)
    name = mongoengine.StringField()
    contactInfo = mongoengine.DictField(required=False)

    @property
    def prefix(self):
        return str(self._id).zfill(3)

    def nextSKU(self):
        objects = product.objects(manufacturer=self).order_by("$natural")
        if objects.count() == 0:
            return f"{self.prefix}00001"
        else:
            lastSKU = objects.first.sku
            lastID = int(lastSKU[3:])
            nextID = str(lastID + 1)
            return f"{self.prefix}{nextID.zfill(5)}"


class category(mongoengine.Document):
    # Category Name ~ Display Name
    name = mongoengine.StringField()
    # Category description, simple text block.
    description = mongoengine.StringField()

    metaData = mongoengine.DictField()

    # Performs a query to find products with this category, for optimization reasons,
    # the products are not stored in the category document.
    def products(self, **kwargs):
        return product.objects(category=self, **kwargs)

    # Same thing, with fields being resolved by a query to allow for reuse of fields.
    def fields(self, **kwargs):
        return fieldStore.objects(category=self, **kwargs)


class product(mongoengine.Document):
    # Products Name
    name = mongoengine.StringField(required=True)
    # Products SKU, generated on the service end.
    sku = mongoengine.StringField(required=True)
    # Products description, simple block of text.
    description = mongoengine.StringField()
    # Ooh the juicy bits
    # Product Data, stored in structure:
    # FieldStoreID: value
    # On product data render, field display will be reconstructed from store.
    productData = mongoengine.DictField()
    # Meta Data, this will be important information on the product at a service level,
    # Stuff like EtsyIDs, and other things that we need to store, but dont want to define
    # a rigid schema for.
    # Do we structure as a simple 1 layer dictionary?
    # Or do we organize based on service.
    # For simplicity we will keep it to 1 layer with descriptive keys.
    metaData = mongoengine.DictField()
    # Products price, will be stored in a fancy format to allow for currency changes
    # Format in JSON:
    # {
    #   "amount": 200,
    #   "currency": "GBP",
    # }
    # TODO: Clarify how pricing is done, Etsy has some complications with this given no decimal orders.
    # Maybe include a boolean in the currency JSON for if sold by unit or by measure?
    # Or should that be included in the db store.
    # Include in DB store to make querying easier.
    # Not done yet ~ Need to actually do.
    price = mongoengine.DictField()

    # We will keep quantity out of the mix for now.
    # TODO: Decide on how stock will be stored, must be considered alongside stockChange
    # quantity = mongoengine.DecimalField(precision=4)

    # Reference Fields
    # Store manufacturer and category.
    manufacturer = mongoengine.ReferenceField(manufacturer, required=True)
    category = mongoengine.ReferenceField(category, required=True)

    def stockChanges(self, **kwargs):
        return stockChange.objects(product=self, **kwargs)


class fieldStore(mongoengine.Document):
    name = mongoengine.StringField()
    fieldType = mongoengine.StringField()
    details = mongoengine.DictField()
    metaData = mongoengine.DictField()  # Corresponding field name in WooCommerce.
    category = mongoengine.ReferenceField(category)

    def Schema(self):
        build = {self.name: {
            **{"type": self.type},
            **self.details,
        }}
        return build


class stockChange(mongoengine.Document):
    state = mongoengine.StringField(default="unapplied")
    time_occurred = mongoengine.DateTimeField(default=datetime.now)

    originPlatform = mongoengine.StringField()
    originPlatformOrderID = mongoengine.StringField()
    originPlatformProductID = mongoengine.StringField()

    quantity = mongoengine.DecimalField()
    action = mongoengine.StringField() # add, subtract, set
    product = mongoengine.ReferenceField(product)