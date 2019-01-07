from Crystal import guesdual
def test():
    path = 'C:\\Users\\ccccc\\PycharmProjects\\Layer_Structure_Caculation\\venv\\geo_opt\\x_-0.150\\z_-0.106'
    inp = guesdual.Guesdual(path)
    string = inp.getstring()
    assert(string == "GUESDUAL \n 1 0 \n 15 10 2")


def testsuite():
    test()
    print("passed")
