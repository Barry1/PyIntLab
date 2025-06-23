from pyintlab import ScalarInterval

Kreditsumme: ScalarInterval = ScalarInterval(240000, 275000)
Monatszins: ScalarInterval = ScalarInterval(3.3, 3.7) / 1200
LaufzeitMonate: ScalarInterval = 12 * ScalarInterval(15, 17)
Rate: ScalarInterval = (
    Kreditsumme * Monatszins / (1 - 1 / (1 + Monatszins) ** LaufzeitMonate)
)
if __name__ == "__main__":
    print(30 * "=", " Kreditrechner ", 30 * "=")
    print("Kreditsumme:", Kreditsumme)
    print("Monatszins:", Monatszins)
    print("Zinssatz:", Monatszins * 12 * 100)
    print("Laufzeit in Monaten:", LaufzeitMonate)
    print("Laufzeit in Jahren:", LaufzeitMonate / 12)
    print(30 * "=", " Ergebnis ", 30 * "=")
    print("Rate:", Rate)
    print("Jahresrate:", Rate * 12)
    print("Gesamtkosten:", Rate * LaufzeitMonate)
