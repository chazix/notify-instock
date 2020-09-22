from csvCustom import CCsvObject

class CProduct(CCsvObject):
    def __init__(self, rooturl=None, name=None, category=None, price=None, desc=None, purl=None, iurl=None):
        self.m_rooturl  = rooturl
        self.m_name     = name
        self.m_category = category
        self.m_price    = price
        self.m_desc     = desc
        self.m_url      = purl
        self.m_image    = iurl

    def FormatCsv(self):
        return '{0};{1};{2};{3};{4};{5};{6}'.format(self.m_rooturl, self.m_name, self.m_category, self.m_price, self.m_desc, self.m_url, self.m_image)

class CProductPage:
    def __init__(self, page):
        self.m_products  = []
        self.m_page      = page
        self.m_success   = False

    def AddProduct(self, product):
        self.m_products.append(product)

    def IsSuccess(self):
        return self.m_success

    def SetSuccess(self):
        self.m_success = True