import React, { useState, useEffect, useRef } from "react";
import Child from './Child';

export default function Parent() {
//   const [isLoading, setLoading] = useState(true);
  const var1 = useRef(0)
  const adder = () => {return var1.current += 1;}

  useEffect(() => {
    async function onLoad() {
      var1.current = var1.current+1;
    }
    onLoad();
  }, );

  return (
    <div className="hi">
      Hello world {var1.current} <Child value={var1} callback={adder} />
    </div>
  );
}
