import mongoengine
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


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
        return str(self.iterID).zfill(3)

    def products(self, **kwargs):
        return product.objects(supplier=self, **kwargs)


class category(mongoengine.Document):
    iterID = mongoengine.SequenceField(primary_key=True)
    name = mongoengine.StringField(required=True)
    description = mongoengine.StringField()
    properties = mongoengine.DictField()
    # ^^^ A dict of all the different properties applicable to this category.
    # Structure of; name: type

    def products(self, **kwargs):
        return product.objects(category=self, **kwargs)


class product(mongoengine.Document):
    iterID = mongoengine.SequenceField(primary_key=True)
    name = mongoengine.StringField(required=True)
    description = mongoengine.StringField()
    productData = mongoengine.DictField()  # A Dict storing productData.
    metaData = mongoengine.DictField()  # A simple dict storing meta like ETSYListingIDs, etc.
    price = mongoengine.DictField()
    quantity = mongoengine.DecimalField(precision=4)

    # Reference Fields
    supplier = mongoengine.ReferenceField(manufacturer, required=True)
    category = mongoengine.ReferenceField(category, required=True)

    @property
    def sku(self):
        return self.supplier.prefix + str(self.iterID).zfill(5)

    def stockChanges(self, **kwargs):
        return stockChange.objects(product=self, **kwargs)


class stockChange(mongoengine.Document):
    product = mongoengine.ReferenceField(product)
    stage = mongoengine.StringField(default="fetch")
    originService = mongoengine.StringField()
    changeType = mongoengine.StringField()
    quantity = mongoengine.DecimalField(precision=4)
    time_created = mongoengine.DateTimeField(default=datetime.utcnow())
