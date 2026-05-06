import sys
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from PyQt5 import QtCore, QtGui, QtWidgets

from pocketfish.config import LOGO_PATH
from pocketfish.overlay import Overlay
from pocketfish.panel import ControlPanel
from pocketfish.startup import StartupDialog
from pocketfish.worker import AssistantWorker


def fmt_score(score) -> str:
    if score is None:
        return "—"
    w = score.white()
    if w.is_mate():
        return f"#{w.mate()}"
    return f"{(w.score(mate_score=10000) or 0)/100:+.2f}"


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(LOGO_PATH))

    startup = StartupDialog()
    if startup.exec_() != QtWidgets.QDialog.Accepted or startup.choice is None:
        sys.exit(0)

    worker = AssistantWorker(
        depth=startup.depth,
        movetime_ms=startup.movetime_ms,
        threads=startup.threads,
        hash_mb=startup.hash_mb,
        skill=startup.skill,
    )

    overlay = Overlay()
    overlay.show()

    panel = ControlPanel()
    panel.apply_engine_settings(
        depth=startup.depth,
        movetime_ms=startup.movetime_ms,
        threads=startup.threads,
        hash_mb=startup.hash_mb,
        skill=startup.skill,
    )

    thread = QtCore.QThread()
    worker.moveToThread(thread)
    thread.started.connect(worker.run)

    panel.colorChanged.connect(worker.set_color)
    panel.debugToggled.connect(worker.set_debug)
    panel.debugToggled.connect(overlay.set_debug)
    panel.suggestionToggled.connect(worker.set_suggestions)
    panel.engineOptsChanged.connect(worker.set_engine_opts)

    worker.statusChanged.connect(panel.set_status)
    worker.moveFound.connect(overlay.set_move)
    worker.moveCleared.connect(overlay.clear_move)
    worker.boardRect.connect(overlay.set_board_rect)
    worker.moveLogged.connect(panel.append_log)
    worker.suggestionText.connect(panel.set_suggestion)

    def on_debug(info: dict) -> None:
        panel.lbl_monitor.setText(str(info.get("monitor") or "—"))
        pos = info.get("pos")
        panel.lbl_pos.setText(f"{pos[0]},{pos[1]}" if pos else "—")
        panel.lbl_size.setText(f"{info.get('size')}px" if info.get("size") else "—")
        panel.lbl_turn.setText(info.get("turn", "—"))
        panel.lbl_fps.setText(f"{info.get('fps', 0):.1f}")
        panel.lbl_eval.setText(fmt_score(info.get("score")))
        panel.lbl_state.setText(info.get("state", "—"))
        panel.lbl_orient.setText("flipped" if info.get("flipped") else "normal")
        panel.fen_edit.setText(info.get("fen", ""))
        pv = info.get("pv") or []
        panel.pv_label.setText("PV: " + " ".join(pv) if pv else "PV: —")
        grid = info.get("grid")
        if grid is not None:
            panel.board_view.set_grid(grid)
        panel.eval_bar.set_eval(info.get("score"))

    worker.debugInfo.connect(on_debug)

    panel.color_combo.blockSignals(True)
    panel.color_combo.setCurrentText(startup.choice)
    panel.color_combo.blockSignals(False)
    worker.confirm_color(startup.choice)

    panel.show()
    thread.start()

    def cleanup() -> None:
        worker.stop()
        thread.quit()
        thread.wait(1500)

    app.aboutToQuit.connect(cleanup)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
