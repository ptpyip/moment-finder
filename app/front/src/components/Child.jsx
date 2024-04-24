import React, { useState, useEffect, useRef } from "react";

export default function Child({value, callback}) {
  const [var1, setVar1] = useState(0);
//   const var1 = useRef(0)

  useEffect(() => {
    async function onLoad() {
      console.log("Child rerender")
    }
    onLoad();
  }, );

  return (
    <div className="child">
      child here <button onClick={(() => {setVar1(var1+1);callback();})}>Increase state value:{var1}</button>
      <div>Value from parent:{value.current}</div>
    </div>
  );
}
