from flask import Blueprint
from flask_restful import Api
from app.api.resources import (
    ProductListResource, ProductResource, 
    OrderListResource, OrderResource, OrderStatusResource,
    CustomerListResource, CustomerResource, CustomerOrdersResource,
    AuthLoginResource, AuthRegisterResource, AuthForgotPasswordResource, AuthResetPasswordResource,
    ShippingMethodListResource, ShippingZoneListResource,
    PromotionListResource, PromotionResource,
    NotificationListResource, NotificationResource, NotificationSettingsResource
)

# Create Blueprint
api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Register API resources
api.add_resource(AuthLoginResource, '/auth/login')
api.add_resource(AuthRegisterResource, '/auth/register')
api.add_resource(AuthForgotPasswordResource, '/auth/forgot-password')
api.add_resource(AuthResetPasswordResource, '/auth/reset-password')

api.add_resource(ProductListResource, '/products')
api.add_resource(ProductResource, '/products/<int:product_id>')

api.add_resource(OrderListResource, '/orders')
api.add_resource(OrderResource, '/orders/<int:order_id>')
api.add_resource(OrderStatusResource, '/orders/<int:order_id>/status')

api.add_resource(CustomerListResource, '/customers')
api.add_resource(CustomerResource, '/customers/<int:customer_id>')
api.add_resource(CustomerOrdersResource, '/customers/<int:customer_id>/orders')

api.add_resource(ShippingMethodListResource, '/shipping/methods')
api.add_resource(ShippingZoneListResource, '/shipping/zones')

api.add_resource(PromotionListResource, '/promotions')
api.add_resource(PromotionResource, '/promotions/<int:promotion_id>')

api.add_resource(NotificationListResource, '/notifications')
api.add_resource(NotificationResource, '/notifications/<int:notification_id>/read')
api.add_resource(NotificationSettingsResource, '/notifications/settings')
