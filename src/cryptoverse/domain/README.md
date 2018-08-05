This folder contains the smart objects to use in an exchange environment. For example Order and Balance objects.

These classes contain a lot of context. For example a Market objects knows about the fees of the specific exchange it is linked to.
In another example the Order object is linked to the exchange where an order will be or already is placed at. The order object
can refresh the state of the order at the exchange. The Order object is also able to derive conclusions from possibly limited input.

This is the top layer that the end-users of this package will use the most.
