TAUX=0.001


def findAngleofAttack(init_verticalSpeed,final_verticalSpeed,init_angleofAttack):
    diffVerticalSpeed=final_verticalSpeed-init_verticalSpeed
    diffVerticalSpeed_abs=abs(final_verticalSpeed-init_verticalSpeed)
    if diffVerticalSpeed>0:
        return init_angleofAttack+(diffVerticalSpeed_abs*TAUX)*init_angleofAttack
    elif diffVerticalSpeed<0:
        return init_angleofAttack-(diffVerticalSpeed_abs*TAUX)*init_angleofAttack
    elif diffVerticalSpeed==0:
        return init_angleofAttack

print(findAngleofAttack(5,10,8.5))