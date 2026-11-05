exec(open('799x-gragus-animation/study.py').read().split('can=')[0])
can=Image.new('RGB',(1200,450))
for k,z in enumerate([20,45,70]):
 q=mul(axis(2,z),mul(axis(0,-100),sample(m['Nodes'][35]['Rotation'],1833,[0,0,0,1])))
 over={35:{'r':q},40:{'r':mul(axis(1,-15),sample(m['Nodes'][40]['Rotation'],1833,[0,0,0,1]))}}
 can.paste(render(1833,over,str(z)),(400*k,0))
can.save('799x-gragus-animation/drink-study2.png')
