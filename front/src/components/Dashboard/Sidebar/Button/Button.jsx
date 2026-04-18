import { useLocation, useNavigate } from "react-router-dom";
import styles from "./button.module.scss";
import { MARKETING_SITE_URL } from "../../../../config";

const Button = ({ active, text, handleButtonClick, link }) => {
  const location = useLocation();
  const navigate = useNavigate();
  active = location.pathname === link;
  return (
    <div
      className={`${styles.Button} ${active ? styles.active : null}`}
      onClick={(e) => {
        if (link) {
          handleButtonClick(text);
          e.preventDefault();
          navigate(`${link}`);
        } else if (MARKETING_SITE_URL) {
          window.open(`${MARKETING_SITE_URL}/process/`, "_self");
        }
      }}
    >
      {text}
    </div>
  );
};
export default Button;
