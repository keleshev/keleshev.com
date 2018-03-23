


module Cortege0 = struct
  type _ t =
    | [] : unit t
    | (::) : 'a * 'b t -> ('a -> 'b) t
end


module type CORTEGE = sig
  type _ t

  val unit : unit t
  val pair : 'a -> 'b -> ('a -> 'b -> unit) t
  val triple : 'a -> 'b -> 'c -> ('a -> 'b -> 'c -> unit) t

  val prepend : 'head -> 'tail t -> ('head -> 'tail) t

  val first  : ('a -> _) t -> 'a
  val second : (_ -> 'a -> _) t -> 'a
  val third  : (_ -> _ -> 'a -> _) t -> 'a

  module Update : sig
    val first : ('a -> 'rest) t
             -> 'x
             -> ('x -> 'rest) t

    val second : ('a -> 'b -> 'tail) t
              -> 'x
              -> ('a -> 'x -> 'tail) t

    val third : ('a -> 'b -> 'c -> 'tail) t
             -> 'x
             -> ('a -> 'b -> 'x -> 'tail) t
  end
end





module Cortege = struct
  type 'x t = 'x Cortege0.t =
    | [] : unit t
    | (::) : 'a * 'b t -> ('a -> 'b) t

  let unit = Cortege0.[]
  let pair a b = Cortege0.[a; b]
  let triple a b c = Cortege0.[a; b; c]

  let prepend head tail = head :: tail

  let first  Cortege0.(x :: _) = x
  let second Cortege0.(_ :: x :: _) = x
  let third  Cortege0.(_ :: _ :: x :: _) = x

  module Update = struct
    let first (a :: rest) x = x :: rest
    let second (a :: b :: rest) x = a :: x :: rest
    let third (a :: b :: c :: rest) x = a :: b :: x :: rest
  end

  let prepend a rest = Cortege0.(a :: rest)
  let swap Cortege0.(a :: b :: rest) = Cortege0.(b :: a :: rest)
  let tail Cortege0.(_ :: rest) = rest
end


module C = (Cortege : CORTEGE)


module Test = struct

  (* creation *)
  assert (Cortege.unit = Cortege.[]);
  assert (Cortege.pair 1 "2" = Cortege.[1; "2"]);
  assert (Cortege.triple 1 2 3 = Cortege.[1; 2; 3]);

  (* comparison *)
  assert (Cortege.[1; "a"; `b] = Cortege.[1; "a"; `b]);
  assert (Cortege.[9; "x"; `z] <> Cortege.[1; "a"; `b]);
  assert (Cortege.[9.0; "x"; `z] <> Cortege.[1.0; "a"; `b]);

  (* pattern-matching *)
  assert begin
    match Cortege.[true; "a"; `b] with
    | Cortege.[true; _; _] -> true
    | Cortege.(false :: _) -> false
  end;

  (* selectors *)
  assert (Cortege.(first [`a]) = `a);
  assert (Cortege.(first [`a; `b]) = `a);
  assert (Cortege.(first [`a; `b; `c]) = `a);
  assert (Cortege.(second [1; 2]) = 2);

  (* update *)
  assert Cortege.(Update.first [1] "x" = ["x"]);
  assert Cortege.(Update.first [1; 2] "x" = ["x"; 2]);
  assert Cortege.(Update.first [1; 2; 3] "x" = ["x"; 2; 3]);

  assert Cortege.(Update.second [1; 2] "x" = [1; "x"]);

  (* prepend *)
  assert (Cortege.(`a :: [`b]) = Cortege.[`a; `b]);

  print_endline " -- ok -- "

end




module Array_backed_cortege : CORTEGE = struct
  type _ t = int array

  let first  t = Obj.magic (Array.unsafe_get t 0)
  let second t = Obj.magic (Array.unsafe_get t 1)
  let third  t = Obj.magic (Array.unsafe_get t 2)

  let prepend head tail = Array.append [|Obj.magic head|] tail

  let unit = [||]
  let pair a b = [|Obj.magic a; Obj.magic b|]
  let triple a b c = [|Obj.magic a; Obj.magic b; Obj.magic c|]

  module Update = struct
    let array_update n array x =
      let array = Array.copy array in
      Array.unsafe_set array 0 x;
      array

    let first array = Obj.magic (array_update 0 (Obj.magic array))
    let second array = Obj.magic (array_update 1 (Obj.magic array))
    let third array = Obj.magic (array_update 2 (Obj.magic array))
  end
end


module Test_array_backed_cortege = struct

  let open Array_backed_cortege in
  let (^) = prepend in

  assert ((1 ^ "a" ^ `b ^ unit) = (1 ^ "a" ^ `b ^ unit));
  assert ((9 ^ "a" ^ `b ^ unit) <> (1 ^ "a" ^ `b ^ unit));

(* The following fails because the unsafe implementation
   above does not consider the float array hack. *)
(* assert ((1.0 ^ "a" ^ `b ^ unit) = (1.0 ^ "a" ^ `b ^ unit)); *)

  (* first/second *)
  assert (first (pair `a `b) = `a);
  assert (second (pair 1 2) = 2);

  (* prepend *)
  assert (`a ^ `b ^ unit = pair `a `b);

  print_endline " -- ok -- "
end
