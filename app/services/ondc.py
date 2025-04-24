"""
ONDC Integration Service

This module provides integration with the Open Network for Digital Commerce (ONDC)
protocol for catalog management, order processing, and logistics.
"""

import os
import json
import requests
from datetime import datetime
from app.models.product import Product
from app.models.order import Order

class OndcService:
    """Service class for ONDC protocol integration."""
    
    def __init__(self, seller_id):
        """Initialize the ONDC service with seller settings."""
        self.seller_id = seller_id
        self.base_url = os.environ.get('ONDC_API_URL', 'https://api.ondc.org/v1')
        self.api_key = os.environ.get('ONDC_API_KEY', '')
        
        # In a real application, you would load these from settings
        self.provider_id = "example_provider_id"
        self.location_id = "example_location_id"
    
    def format_product_for_ondc(self, product):
        """Format product data according to ONDC catalog format."""
        return {
            "id": str(product.id),
            "descriptor": {
                "name": product.name,
                "short_desc": product.short_description,
                "long_desc": product.description,
                "images": [img.image_path for img in product.images]
            },
            "price": {
                "currency": "INR",
                "value": str(product.price),
                "maximum_value": str(product.mrp)
            },
            "category_id": product.ondc_category,
            "fulfillment_id": product.fulfillment_id,
            "location_id": self.location_id,
            "provider_id": self.provider_id,
            "@ondc/org/statutory_reqs_packaged_commodities": {
                "manufacturer_or_packer_name": self.provider_id,
                "common_or_generic_name_of_commodity": product.name,
                "net_quantity_or_measure_of_commodity_in_pkg": "1",
                "manufacturer_or_packer_address": "Provider Address"
            }
        }
    
    def publish_catalog(self):
        """Publish the catalog to ONDC network."""
        products = Product.query.filter_by(seller_id=self.seller_id, status='active').all()
        
        catalog = {
            "context": {
                "domain": "nic2004:52110",
                "action": "catalog",
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat()
            },
            "catalog": {
                "descriptor": {
                    "name": "Seller Catalog"
                },
                "providers": [
                    {
                        "id": self.provider_id,
                        "descriptor": {
                            "name": "Seller Name"
                        },
                        "locations": [
                            {
                                "id": self.location_id
                            }
                        ],
                        "items": [self.format_product_for_ondc(p) for p in products]
                    }
                ]
            }
        }
        
        # In a real application, you would make an API call to ONDC
        # response = requests.post(
        #     f"{self.base_url}/catalog",
        #     json=catalog,
        #     headers={"Authorization": f"Bearer {self.api_key}"}
        # )
        
        # return response.json()
        
        # For demonstration purposes
        return {"status": "success", "message": "Catalog published successfully"}
    
    def accept_order(self, order_id):
        """Accept an order from ONDC network."""
        order = Order.query.filter_by(id=order_id, seller_id=self.seller_id).first()
        if not order:
            return {"status": "error", "message": "Order not found"}
        
        order_acceptance = {
            "context": {
                "domain": "nic2004:52110",
                "action": "on_confirm",
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat()
            },
            "order": {
                "id": order.ondc_order_id,
                "state": "Accepted",
                "provider": {
                    "id": self.provider_id
                },
                "items": [
                    {
                        "id": item.product_id,
                        "quantity": {
                            "count": item.quantity
                        }
                    } for item in order.items
                ],
                "fulfillments": [
                    {
                        "id": "fulfillment-1",
                        "type": "Delivery",
                        "tracking": True,
                        "state": {
                            "descriptor": {
                                "code": "Pending"
                            }
                        }
                    }
                ]
            }
        }
        
        # In a real application, you would make an API call to ONDC
        # response = requests.post(
        #     f"{self.base_url}/on_confirm",
        #     json=order_acceptance,
        #     headers={"Authorization": f"Bearer {self.api_key}"}
        # )
        
        # if response.status_code == 200:
        #     order.status = 'processing'
        #     db.session.commit()
        #     return response.json()
        
        # For demonstration purposes
        return {"status": "success", "message": "Order accepted successfully"}
    
    def update_order_status(self, order_id, status):
        """Update order status in ONDC network."""
        order = Order.query.filter_by(id=order_id, seller_id=self.seller_id).first()
        if not order:
            return {"status": "error", "message": "Order not found"}
        
        # Map internal status to ONDC status
        ondc_status_map = {
            "processing": "Accepted",
            "shipped": "In-transit",
            "delivered": "Delivered",
            "cancelled": "Cancelled"
        }
        
        if status not in ondc_status_map:
            return {"status": "error", "message": "Invalid status"}
        
        status_update = {
            "context": {
                "domain": "nic2004:52110",
                "action": "on_status",
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat()
            },
            "order": {
                "id": order.ondc_order_id,
                "state": ondc_status_map[status],
                "provider": {
                    "id": self.provider_id
                },
                "items": [
                    {
                        "id": item.product_id,
                        "quantity": {
                            "count": item.quantity
                        }
                    } for item in order.items
                ],
                "fulfillments": [
                    {
                        "id": "fulfillment-1",
                        "type": "Delivery",
                        "tracking": True,
                        "state": {
                            "descriptor": {
                                "code": ondc_status_map[status]
                            }
                        }
                    }
                ]
            }
        }
        
        # In a real application, you would make an API call to ONDC
        # response = requests.post(
        #     f"{self.base_url}/on_status",
        #     json=status_update,
        #     headers={"Authorization": f"Bearer {self.api_key}"}
        # )
        
        # For demonstration purposes
        return {"status": "success", "message": f"Order status updated to {status} successfully"}
    
    def query_logistics_providers(self, pickup_location, delivery_location):
        """Query available logistics providers for an order."""
        logistics_query = {
            "context": {
                "domain": "nic2004:52110",
                "action": "search",
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat()
            },
            "message": {
                "intent": {
                    "fulfillment": {
                        "type": "Delivery",
                        "start": {
                            "location": pickup_location
                        },
                        "end": {
                            "location": delivery_location
                        }
                    }
                }
            }
        }
        
        # In a real application, you would make an API call to ONDC
        # response = requests.post(
        #     f"{self.base_url}/search",
        #     json=logistics_query,
        #     headers={"Authorization": f"Bearer {self.api_key}"}
        # )
        
        # For demonstration purposes
        return {
            "providers": [
                {"id": "logistics-1", "name": "Fast Delivery", "price": 50},
                {"id": "logistics-2", "name": "Standard Delivery", "price": 30},
                {"id": "logistics-3", "name": "Economy Delivery", "price": 20}
            ]
        }
