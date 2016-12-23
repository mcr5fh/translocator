from translocController import TranslocController
t = TranslocController()
#res = t.get_next_bus_arrival(347, 4123822)
# t.set_location("608 Preston Pl, Charlottesville, VA 22903")
t.set_closest_stop("608 Preston Pl, Charlottesville, VA 22903")
print(t.get_closest_stop_list())