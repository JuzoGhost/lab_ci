from unittest.mock import Mock

import pytest

from shop.cart import Cart


# 1. Тести додавання товарів та підрахунку (Параметризація)
@pytest.mark.parametrize(
    "name, price, qty, expected_count",
    [
        ("notebook", 50.0, 1, 1),
        ("pencil", 10.0, 5, 5),
        ("eraser", 5.0, 10, 10),
    ],
)
def test_add_item_increases_count(
    empty_cart: Cart, name: str, price: float, qty: int, expected_count: int
) -> None:
    empty_cart.add(name, price, qty)
    assert empty_cart.items_count() == expected_count


def test_add_existing_item_updates_qty(cart_with_items: Cart) -> None:
    cart_with_items.add("book", price=200.0, qty=3)
    assert cart_with_items.items_count() == 9  # 2 старі + 3 нові + 4 ручки


# 2. Перевірка винятків (від'ємна ціна, нульова кількість, некоректна знижка, курс, видалення)
def test_add_negative_price_raises(empty_cart: Cart) -> None:
    with pytest.raises(ValueError, match="price must be non-negative"):
        empty_cart.add("book", price=-10.0)


def test_add_zero_qty_raises(empty_cart: Cart) -> None:
    with pytest.raises(ValueError, match="qty must be positive"):
        empty_cart.add("book", price=100.0, qty=0)


def test_remove_missing_item_raises(empty_cart: Cart) -> None:
    with pytest.raises(KeyError):
        empty_cart.remove("nonexistent")


def test_total_with_invalid_discount_raises(cart_with_items: Cart) -> None:
    with pytest.raises(ValueError, match="discount_percent must be in \\[0, 100\\]"):
        cart_with_items.total(discount_percent=150.0)


def test_total_in_with_invalid_rate_raises(cart_with_items: Cart) -> None:
    rates = Mock()
    rates.get_rate.return_value = -5.0
    with pytest.raises(ValueError, match="rate must be positive"):
        cart_with_items.total_in("USD", rates)


# 3. Тестування видалення
def test_remove_item(cart_with_items: Cart) -> None:
    cart_with_items.remove("book")
    assert cart_with_items.items_count() == 4


# 4. Параметризований тест із граничними значеннями для знижки
@pytest.mark.parametrize(
    "discount, expected_total",
    [
        (0, 460.0),  # Без знижки: (200*2) + (15*4)
        (10, 414.0),  # 10% знижка
        (50, 230.0),  # 50% знижка
        (100, 0.0),  # 100% знижка (граничне)
    ],
)


# 5. Тест із тестовим дублером (Mock)
def test_total_in_currency(cart_with_items: Cart) -> None:
    rates = Mock()
    rates.get_rate.return_value = 40.0  # 1 USD = 40 UAH
    # 460 / 40 = 11.5
    assert cart_with_items.total_in("USD", rates) == pytest.approx(11.5)
    rates.get_rate.assert_called_once_with("USD")


# 6. TDD: Тести для нового методу most_expensive
def test_most_expensive_empty_cart(empty_cart: Cart) -> None:
    assert empty_cart.most_expensive() is None


def test_most_expensive_with_items(cart_with_items: Cart) -> None:
    most_expensive = cart_with_items.most_expensive()
    assert most_expensive is not None
    assert most_expensive.name == "book"


def test_most_expensive_updates_price_on_same_name(empty_cart: Cart) -> None:
    empty_cart.add("apple", 10.0)
    empty_cart.add("apple", 50.0)  # Заміна ціни
    most_expensive = empty_cart.most_expensive()
    assert most_expensive is not None
    assert most_expensive.price == 50.0
