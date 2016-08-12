import sys, argparse, time
from ev3dev import *

lmotor = large_motor(OUTPUT_B); assert lmotor.connected
rmotor = large_motor(OUTPUT_D); assert rmotor.connected
cmotor = medium_motor(OUTPUT_C); assert cmotor.connected
ls     = light_sensor();        assert ls.connected
cs     = color_sensor();        assert cs.connected
ts     = touch_sensor();        assert ts.connected
rs     = infrared_sensor();	assert rs.connected
cs.mode = 'COL-COLOR'
lmotor.speed_regulation_enabled = 'on'
rmotor.speed_regulation_enabled = 'on'
cmotor.speed_regulation_enabled = 'on'


white = 481.8
black = 310
mid   = 396

rozmiar = 5
bufor = [0,0,0,0,0]

#czarny = 1
#niebieski = 2
#zielony = 3
#zolty = 4
#czerwony = 5
#bialy = 6

def czarnyBufor(tab):   #ustawia bufor na czarne wartosci, zeby uniknac problemow przy powrocie na czarna linie
    for i in range(0, rozmiar):
        tab[i] = 1

#ignoruj powpoduje omijanie rozjazdów w innym kolorze niz aktualnie pozadany
def ignoruj(m, n, a, t): #t - czas jechania do przodu
        if(m==n and m==3 and (a==4 or a==5)): #jesli szuka zielonego a trafi na 4 lub 5
                jedztrochewlewo(t)
        elif (m==n and m==4 and(a==3 or a==5)): #jesli szuka zoltego a trafi na 3 lub 5
                jedztrochewlewo(t)
        elif (m==n and m==5 and(a==3 or a==4)): #jesli szuka czerwonego a trafi na 3 lub 5
                jedztrochewlewo(t)
        elif( ((m==5 and n==4) or (m==4 and n==5)) and a==3): #jesli szuka czerw. lub zoltego a trafi na zielony
                jedztrochewlewo(t)

def przesun(tab): #przesuwa w lewo bufor

    for i in range(0, rozmiar-1):
        tab[i] = tab[i+1]
    tab[rozmiar-1] = 0

def jednolite(tab): #sprawdza jednolitosc buforu i zwraca jego wartosc jesli jest jednolity

	for i in range(0, rozmiar-1):
                if tab[0]!=tab[i+1]:
                    return -1
	
	else: return tab[0]

def operacja(m): #m==-1 powpoduje opuszczenie chwytaka
        print("Wszedlem do operacja")
        cmotor.run_forever( speed_sp=m*250)
        time.sleep(0.5)
        cmotor.run_forever( speed_sp=0)

def jedztrochewlewo(czas): #funkcja potrzebna jak wykryje zielony rozjazd, obroci sie w lewo w poszukiwaniu linii, nic nie wykryje, potem bedzie obracac
                           #sie w prawo i wykryje czarny - zeby zaczal jechac po czarnej od lewej strony
    lmotor.run_forever( speed_sp=-150)
    rmotor.run_forever( speed_sp=-200)

    time.sleep(czas)
   
def lineFollow(m,n):	#jedzie po linii czarnej dopoki nie napotka koloru m lub n

        global bufor
        zeruj()
        czarnyBufor(bufor)  #ustawia czarny bufor
        print("Wszedlem do lineFollow()")
        integral   = 0
	correction = 0
	derivative = 0
	last_error = 0
        error = 0
        a = 0
        zerujBufor()
        while not ts.value():
                print(rs.value())
		error= mid - ls.value()
   		integral = integral + error
   		derivative = error - last_error
    		last_error = error
                correction = int(0.8*error + 0.025 * integral + 3 * derivative) 

                lmotor.run_forever( speed_sp=int(-(80-correction)) )
                rmotor.run_forever( speed_sp=int(-(80+correction)) )

                bufor[rozmiar-1]=cs.value()

                a=jednolite(bufor)

                if a == m or a == n:
                    return a			#znaleziono szukany kolor

                ignoruj(m, n, a, 0.9)
                przesun(bufor)
                time.sleep(0.01)

def zeruj():    #zeruje predkosci silnikow
	lmotor.run_forever( speed_sp=0)
	rmotor.run_forever( speed_sp=0)

#funkcja obraca robota w lewo lub w prawo przez pewien czas LUB do napotkania czarnej linii LUB plytki kolorowej
def obracanie(k, t, bezw):			#if k == 1: w lewo else: w prawo; t - jakis czas obracania; bezw - czas obrotu bezwarunkowego
        print("Wszedlem do obracanie()")
        lmotor.run_forever( speed_sp=k*150) #obroc sie troche zeby zejsc z czarnej linii
	rmotor.run_forever( speed_sp=k*(-150))	
	time.sleep(bezw)
	zeruj() #daje znak na sekunde jak skonczy obrot bezwarunkowy
        time.sleep(1)
	
        if k==1:
                lmotor.run_forever( speed_sp=100)
                rmotor.run_forever( speed_sp=100)
                time.sleep(0.5)
        else:
                lmotor.run_forever( speed_sp=-100)
                rmotor.run_forever( speed_sp=-100)
                time.sleep(0.5)
	a=0
        b=0
        zerujBufor()
        while b != 1 and b != 5 and b != 4 and a < int(t): #obracaj do napotkania 1, 5 lub 4 przez pewien czas
                przesun(bufor)

                bufor[rozmiar-1]=cs.value()
                b=jednolite(bufor)
                print(bufor)
                lmotor.run_forever( speed_sp=k*100)
		rmotor.run_forever( speed_sp=k*(-100))
                time.sleep(0.01)		
		a+=1

	lmotor.run_forever( speed_sp=0)
	rmotor.run_forever( speed_sp=0)
        return bufor[0]

def zerujBufor():
	for i in range(0, rozmiar): bufor[i]=0

def szukajLinii(): #szuka czegos po napotkaniu na zielony i zwraca to cos

        print("Wszedlem do szukajLinii()")
	lmotor.run_forever( speed_sp=-150) #jedz troche naprzod
        rmotor.run_forever( speed_sp=-150)
        time.sleep(1.8)
        zeruj()
	target = 0 		#kolor plytki z pilka
        x = obracanie(1, 150, 0.4) #napotkany kolor przy obrocie w lewo
        print("Obracam w lewo i widze: ")
        print(x)
	if x == 6:  			#jesli bialy

                y = obracanie(-1, 200, 2.5) 			#napotkany kolor przy obrocie w prawo
                if y == 1:              #jesli czarny to jedz do pola nebieskiego lub czerwonego
                        zeruj()
                        time.sleep(1)
                        print("Wykrylem czarny przy obrocie w prawo")
                        jedztrochewlewo(0.6)
                        return y
                elif y == 5 or y == 4: 		#spotkano plytke z pilka
			return y		

	elif x == 1:
		return x

	elif x == 5: 			#spotkano plytke czerwona 	
		return x

        elif x == 4:			#jezeli zolty
		return x


def zlapPilke(kol):
    granica = 7 #wartosc krytyczna rs.value dla ktorej uznaje ze ma przed soba pilke

    print("Wszedlem do zlapPilke()")
    while rs.value()>granica: #dopoki wartosc czujnika wieksza od jakiejs tam

        zerujBufor()
        while jednolite(bufor)!=6 and rs.value()>granica: #w lewo
            lmotor.run_forever( speed_sp=100)
            rmotor.run_forever( speed_sp=-100)
            przesun(bufor)
            bufor[rozmiar-1] = cs.value()
        if rs.value()<granica: break
        lmotor.run_forever( speed_sp=-100) #troszke naprzod
        rmotor.run_forever( speed_sp=-100)
        time.sleep(0.5)

        skrec(-1, kol) #skrec zeby znalezc sie znow nad plytka o kolorze kol

        zerujBufor()
        while jednolite(bufor)!=6 and rs.value()>granica: #w prawo
            lmotor.run_forever( speed_sp=-100)
            rmotor.run_forever( speed_sp=100)
            przesun(bufor)
            bufor[rozmiar-1] = cs.value()

        if rs.value()<granica: break
        lmotor.run_forever( speed_sp=-100) #troszke naprzod
        rmotor.run_forever( speed_sp=-100)
        time.sleep(0.5)
        skrec(10, kol)
    zeruj()
    operacja(-1)
    time.sleep(1)
    if kol == 4:
        nawracanieNaTrzyZolte()

    elif kol==5:
        nawracanieNaTrzyCzerwone()

    else:
        nawracanieNaTrzy()




def nawracanieNaTrzy():	#metoda powodująca powrót robota z płytki na czarną linię

        print "wszedlem do nawracania"



        lmotor.run_forever( speed_sp=  200) #obroc sie w lewo
        rmotor.run_forever( speed_sp=  -200)
        time.sleep(1.5)

        zerujBufor()

        while ls.value()>340: #dopoki nie jest nad czarnym

            lmotor.run_forever( speed_sp= -100)
            rmotor.run_forever( speed_sp= -100)
            przesun(bufor)
            bufor[rozmiar-1]=cs.value()
        zeruj()
        time.sleep(1.5)

def nawracanieNaTrzyZolte():	#metoda powodująca powrót robota z płytki żółtej na czarną linię

        global bufor
        print "wszedlem do nawracania dla zoltej plytki"
        zeruj()
        lmotor.run_forever( speed_sp=  -200) #obroc sie w lewo
        rmotor.run_forever( speed_sp=   200)
        time.sleep(1.5)

        zerujBufor()


        while ls.value()>340: #dopoki nie jest nad czarnym

            lmotor.run_forever( speed_sp= -100)
            rmotor.run_forever( speed_sp= -100)
            przesun(bufor)
            bufor[rozmiar-1]=cs.value()
        zeruj()
        time.sleep(1.5)

def nawracanieNaTrzyCzerwone():	#metoda powodująca powrót robota z płytki czerwonej na czarną linię 
    global bufor
    zeruj()
    lmotor.run_forever( speed_sp=  200) #obroc sie w lewo
    rmotor.run_forever( speed_sp=  - 200)
    time.sleep(0.5)


    while ls.value()>340: #dopoki nie jest nad czarnym

        lmotor.run_forever( speed_sp= -100)
        rmotor.run_forever( speed_sp= -100)
        przesun(bufor)
        bufor[rozmiar-1]=cs.value()
    zeruj()
    time.sleep(1.5)



def skrec(k,kol): #skreca w lewo lub prawo do momentu az nie znajdzie sie nad kol
    zerujBufor()
    zeruj()
    if k==-1:            #w prawo
        while jednolite(bufor)!=kol:
            lmotor.run_forever( speed_sp=-100)
            rmotor.run_forever( speed_sp=100)
            przesun(bufor)
            bufor[rozmiar-1]=cs.value()

    else:               #w lewo
        while jednolite(bufor)!=kol:
            lmotor.run_forever( speed_sp=100)
            rmotor.run_forever( speed_sp=-100)
            przesun(bufor)
            bufor[rozmiar-1]=cs.value()



while not ts.value(): time.sleep(0.1)		#start na przycisk 
time.sleep(2)

#tmp to kolor pierwszej plytki
#tmp3 to kolor drugiej plytki
#tmp2 i tmp4 to zmienne pomocniczne


lineFollow(3, 3) #jedz po czarnej do napotkania zielonego
tmp = 0
tmp = szukajLinii() #znaleziony kolor (albo od razu znajdzie plytke albo najpierw dojedzie po czarnej)
print ("Po wyjsciu z szukajLinii() tmp = %d", tmp)
if tmp==1:
        print("Wszedlem do tmp==1")
        tmp=lineFollow(5, 4) #jedz czerwonego lub zoltego


print ("Tmp = %d", tmp)
zlapPilke(tmp)

lineFollow(tmp, tmp)
tmp2 = szukajLinii()

if tmp2 == 1:
    lineFollow(tmp, tmp)

zeruj()
time.sleep(1)
operacja(1)
time.sleep(2)

################################druga pilka
nawracanieNaTrzy()


lineFollow(3, 3) #jedz po czarnej do napotkania zielonego po raz drugi

tmp3 = szukajLinii()
if tmp3==1:
        print("Wszedlem do tmp==1")
        tmp3=lineFollow(5, 4) #jedz czerwonego lub zoltego


while tmp3==tmp:
    nawracanieNaTrzy()
    lineFollow(3, 3) #jedz po czarnej do napotkania zielonego po raz drugi
    tmp3 = szukajLinii()
    if tmp3==1:
            print("Wszedlem do tmp==1")
            tmp3=lineFollow(5, 4) #jedz czerwonego lub zoltego



zlapPilke(tmp3)
lineFollow(tmp3, tmp3)
tmp4 = szukajLinii()

if tmp4 == 1:
    lineFollow(tmp3, tmp3)

zeruj()
time.sleep(1)
operacja(1)
time.sleep(1)


	
