class HelmetViolationChecker:
    def check_single(self, person_box, bikes, helmets):
        px1, py1, px2, py2 = person_box
        person_h = py2 - py1
        head_y_limit = py1 + int(0.4 * person_h)

        no_helmet = False

        # -------------------
        # HELMET CHECK
        # -------------------
        for hx1, hy1, hx2, hy2, label, _ in helmets:
            cx = (hx1 + hx2) // 2
            cy = (hy1 + hy2) // 2

            if px1 <= cx <= px2 and py1 <= cy <= head_y_limit:
                if label == "WITHOUT_HELMET":
                    no_helmet = True
                    break

        if not no_helmet:
            return None

        # -------------------
        # BIKE ASSOCIATION
        # -------------------
        person_cx = (px1 + px2) // 2

        for bx1, by1, bx2, by2, _ in bikes:
            if bx1 <= person_cx <= bx2:
                return (bx1, by1, bx2, by2)

        return None
