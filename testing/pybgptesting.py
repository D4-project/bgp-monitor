import pybgpstream


if __name__ == "__main__":
    stream = pybgpstream.BGPStream(project="ris-live", collector="rrc00")

    for e in stream:
        print(e)
