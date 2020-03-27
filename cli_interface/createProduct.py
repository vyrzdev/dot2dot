import npyscreen
import database


class productCreator(npyscreen.NPSApp):
    def main(self):
        self.StandardProductForm = npyscreen.Form(name="Create a Product.", columns3=100)
        self.metaForm = npyscreen.Form(name="Get MetaData.")

        name = self.StandardProductForm.add(npyscreen.TitleText, name="Product Name:")
        # description = self.StandardProductForm.add(npyscreen.MultiLineEdit, max_height=5, name="Description:")
        price = self.StandardProductForm.add(npyscreen.TitleText, name="Price:", width=100)
        quantity = self.StandardProductForm.add(npyscreen.TitleText, name="Quantity:")
        manufacturer = self.StandardProductForm.add(npyscreen.TitleSelectOne,
                                                    max_height=10,
                                                    name="Manufacturer:",
                                                    scroll_exit=True,
                                                    values=[x.name for x in list(database.models.manufacturer.objects())],
                                                    )
        category = self.StandardProductForm.add(npyscreen.TitleSelectOne,
                                           max_height=10,
                                           name="Category: ",
                                           values=[x.name for x in list(database.models.category.objects())],
                                           scroll_exit=True
                                           )
        self.StandardProductForm.edit()
        category = database.models.category.objects(name=category.get_selected_objects()[0]).first()
        metaDict = dict()
        for field in category.properties.keys():
            metaDict[field] = self.metaForm.add(npyscreen.TitleText, name=field)
        self.metaForm.edit()
        productData = {field: metaDict[field].value for field in metaDict.keys()}
        self.productObj = database.models.product(name=name.value,
                                                  price={"currency": "GBP", "amount": int(price.value)},
                                                  quantity=float(quantity.value),
                                                  supplier=database.models.manufacturer.objects(name=manufacturer.get_selected_objects()[0]).first(),
                                                  productData=productData,
                                                  category=category
        )
        self.productObj.save()
