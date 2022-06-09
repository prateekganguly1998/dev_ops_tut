from flask_restx import Namespace, Resource, fields
from ..models.orders import Order
from ..models.users import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from http import HTTPStatus
from ..utils import db

order_namespace = Namespace('orders', description="a namespace for orders")

order_model = order_namespace.model(
    'Order', {
        'id': fields.Integer(description="An ID"),
        'quantity': fields.Integer(description="quantity"),
        'flavour': fields.String(description="Flavour"),
        'size': fields.String(description="Size of order", required=True,
                              enum=['SMALL', 'MEDIUM', 'LARGE', 'EXTRA_LARGE']
                              ),
        'order_status': fields.String(description="The status of the Order",
                                      required=True, enum=['PENDING',
                                                           'IN_TRANSIT',
                                                           'DELIVERED']
                                      )
    }
)

order_status_model = order_namespace.model(
    'OrderStatus', {
        'order_status': fields.String(description="Order status",
                                      enums=['PENDING',
                                             'IN_TRANSIT',
                                             'DELIVERED'])
    }
)


@order_namespace.route('/orders')
class OrderGetCreate(Resource):
    @order_namespace.marshal_list_with(order_model)
    @jwt_required()
    def get(self):
        """
        Get all orders
        """
        orders = Order.query.all()

        return orders, HTTPStatus.OK

    @order_namespace.expect(order_model)
    @jwt_required()
    @order_namespace.marshal_with(order_model)
    def post(self):
        """
        Place a new order
        """
        data = order_namespace.payload
        username = get_jwt_identity()
        current_user = User.query.filter_by(username=username).first()
        new_order = Order(size=data['size'],
                          quantity=data['quantity'],
                          flavour=data['flavour'],
                          )
        new_order.user = current_user

        new_order.save()
        return new_order, HTTPStatus.CREATED


@order_namespace.route('/order/<int:order_id>')
class GetUpdateDelete(Resource):

    @order_namespace.marshal_with(order_model)
    @jwt_required()
    def get(self, order_id):
        """
            Retrieve an order by id
        """
        order = Order.get_by_id(order_id)

        return order, HTTPStatus.OK

    @order_namespace.expect(order_model)
    @order_namespace.marshal_with(order_model)
    @jwt_required()
    def put(self, order_id):
        """
            Update an order by id
        """
        order_to_update = Order.get_by_id(order_id)
        data = order_namespace.payload
        if data['quantity']:
            order_to_update.quantity = data['quantity']
        if data['size']:
            order_to_update.size = data['size']
        if data['flavour']:
            order_to_update.flavour = data['flavour']

        db.session.commit()

        return order_to_update, HTTPStatus.OK

    @jwt_required()
    @order_namespace.marshal_with(order_model)
    def delete(self, order_id):
        """
            Delete an order by id
        """
        order_to_delete = Order.get_by_id(order_id)

        order_to_delete.delete()
        return order_to_delete, HTTPStatus.OK


@order_namespace.route('/user/<int:user_id>/order/<int:order_id>/')
class GetOrderByUser(Resource):
    @order_namespace.marshal_with(order_model)
    @jwt_required()
    def get(self, user_id, order_id):
        """
            Get user specific order
        """
        user = User.get_by_id(user_id)
        order = Order.query.filter_by(id=order_id).filter_by(user=user).first()

        return order, HTTPStatus.OK


@order_namespace.route('/user/<int:user_id>/orders')
class UserOrders(Resource):
    @order_namespace.marshal_list_with(order_model)
    @jwt_required()
    def get(self, user_id):
        """
            Get all orders of an user
        """
        user = User.get_by_id(user_id)
        orders = user.orders
        return orders, HTTPStatus.OK


@order_namespace.route('/order/status/<int:order_id>')
class UpdateOrderStatus(Resource):
    @order_namespace.expect(order_status_model)
    @order_namespace.marshal_with(order_model)
    @jwt_required()
    def patch(self, order_id):
        """
            Update an order's status
        """
        data = order_namespace.payload
        order_to_update = Order.get_by_id(order_id)
        order_to_update.order_status = data['order_status']

        db.session.commit()

        return order_to_update, HTTPStatus.OK
